"""
Dashboard-facing Slack endpoints (API-key protected, see router.py) and the
signed interactivity webhook (Slack-signature protected).
"""

import json
from dataclasses import dataclass
from urllib.parse import parse_qs

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.core.errors import ConflictError
from backend.core.limiter import limiter
from backend.db.session import get_db
from backend.logging import logger
from backend.schemas.slack import SlackNotifyOut, SlackStatusOut, SlackTestOut
from backend.security.slack import is_valid_slack_signature
from backend.services import approval_service, slack_service

router = APIRouter(prefix="/slack", tags=["slack"])
webhook_router = APIRouter(prefix="/slack", tags=["slack"])

DEFAULT_SLACK_REJECTION_REASON = "Rejected via Slack"
APPROVE, REJECT = "approve_incident", "reject_incident"


@dataclass(frozen=True)
class SlackAction:
    action_id: str
    incident_id: int
    actioned_by: str
    response_url: str | None


def _bad_request(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_400_BAD_REQUEST, detail)


def _verify_signature(request: Request, raw_body: bytes) -> None:
    ok = is_valid_slack_signature(
        signing_secret=get_settings().slack_signing_secret,
        request_body=raw_body,
        timestamp_header=request.headers.get("X-Slack-Request-Timestamp"),
        signature_header=request.headers.get("X-Slack-Signature"),
    )
    if not ok:  # same 401 for every failure reason, on purpose
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Slack signature")


def _parse_action(raw_body: bytes) -> SlackAction:
    payload_raw = parse_qs(raw_body.decode("utf-8")).get("payload", [None])[0]
    if payload_raw is None:
        raise _bad_request("Missing Slack payload")
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        raise _bad_request("Malformed Slack payload") from None

    actions = payload.get("actions") or []
    if not actions:
        raise _bad_request("No action in Slack payload")

    action_id = actions[0].get("action_id")
    if action_id not in (APPROVE, REJECT):
        raise _bad_request(f"Unknown Slack action_id: {action_id}")
    try:
        incident_id = int(actions[0].get("value"))
    except (TypeError, ValueError):
        raise _bad_request("Invalid incident id in Slack payload") from None

    user_id = (payload.get("user") or {}).get("id") or "unknown"
    return SlackAction(action_id, incident_id, f"slack:{user_id}", payload.get("response_url"))


def _apply_action(db: Session, a: SlackAction) -> tuple[str, list[dict]]:
    """Sync DB work, run in a worker thread. Builds blocks while the session is open."""
    if a.action_id == APPROVE:
        incident, _, _ = approval_service.approve_incident(db, a.incident_id, a.actioned_by)
        text = f"Incident #{a.incident_id} approved and remediated by {a.actioned_by}."
        outcome = f":white_check_mark: *Approved* by {a.actioned_by} — remediation executed."
    else:
        incident, _ = approval_service.reject_incident(
            db, a.incident_id, a.actioned_by, DEFAULT_SLACK_REJECTION_REASON
        )
        text = f"Incident #{a.incident_id} rejected by {a.actioned_by}."
        outcome = f":no_entry: *Rejected* by {a.actioned_by}."
    logger.info("slack_action_applied", action=a.action_id,
                incident_id=a.incident_id, actioned_by=a.actioned_by)
    return text, slack_service.build_outcome_blocks(incident, outcome)


# ---- dashboard-facing -----------------------------------------------------
@router.get("/status", response_model=SlackStatusOut)
@limiter.limit("30/minute")
def slack_status(request: Request) -> SlackStatusOut:
    return SlackStatusOut(**slack_service.get_status())


@router.post("/test", response_model=SlackTestOut)
@limiter.limit("5/minute")
def slack_test(request: Request) -> SlackTestOut:
    return SlackTestOut(ok=True, **slack_service.send_test_message())


@router.post("/notify/{incident_id}", response_model=SlackNotifyOut)
@limiter.limit("10/minute")
def slack_notify(
    request: Request, incident_id: int, force: bool = False, db: Session = Depends(get_db)
) -> SlackNotifyOut:
    approval, already_sent = slack_service.notify_approval_requested(
        db, incident_id, force=force
    )
    return SlackNotifyOut(
        incident_id=incident_id,
        approval_request_id=approval.id,
        channel=approval.slack_channel or "",
        ts=approval.slack_message_ts or "",
        already_sent=already_sent,
    )


# ---- Slack webhook (signature-verified, exempt from IP rate limit) ---------
@webhook_router.post("/actions")
@limiter.exempt
async def slack_actions(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> dict:
    raw_body = await request.body()
    _verify_signature(request, raw_body)
    action = _parse_action(raw_body)

    try:
        text, blocks = await run_in_threadpool(_apply_action, db, action)
    except ConflictError as exc:
        # Already decided elsewhere: tell only the clicker, no error icon in Slack.
        background_tasks.add_task(
            slack_service.update_via_response_url,
            action.response_url,
            {"response_type": "ephemeral", "replace_original": False,
             "text": f":warning: {exc.detail}"},
        )
        return {"text": exc.detail}

    background_tasks.add_task(
        slack_service.update_via_response_url,
        action.response_url,
        {"replace_original": True, "text": text, "blocks": blocks},
    )
    return {"text": text}