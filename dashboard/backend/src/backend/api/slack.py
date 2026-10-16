"""
Slack interactivity webhook — approve/reject buttons on the incident
notification message call back here. Reuses approval_service directly so
Slack and the dashboard go through the exact same idempotency-guarded logic.
"""

import json
from urllib.parse import parse_qs

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.limiter import limiter
from backend.core.logging import logger
from backend.db.session import get_db
from backend.schemas.slack import SlackNotifyOut, SlackStatusOut, SlackTestOut
from backend.security.slack import is_valid_slack_signature
from backend.services import approval_service, slack_service

router = APIRouter(prefix="/slack", tags=["slack"])

DEFAULT_SLACK_REJECTION_REASON = "Rejected via Slack"


@router.get("/status", response_model=SlackStatusOut)
@limiter.limit("30/minute")
def slack_status(request: Request) -> SlackStatusOut:
    """What is configured. Never returns the token or the signing secret."""
    return SlackStatusOut(**slack_service.get_status())


@router.post("/test", response_model=SlackTestOut)
@limiter.limit("5/minute")
def slack_test(request: Request) -> SlackTestOut:
    """Post a test message to the configured channel."""
    result = slack_service.send_test_message()
    return SlackTestOut(ok=True, **result)


@router.post("/notify/{incident_id}", response_model=SlackNotifyOut)
@limiter.limit("10/minute")
def slack_notify(
    request: Request,
    incident_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
) -> SlackNotifyOut:
    """Send (or, with force=true, re-send) the approval request to Slack."""
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


@router.post("/actions")
@limiter.limit("20/minute")
async def slack_actions(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    settings = get_settings()
    raw_body = await request.body()

    valid = is_valid_slack_signature(
        signing_secret=settings.slack_signing_secret,
        request_body=raw_body,
        timestamp_header=request.headers.get("X-Slack-Request-Timestamp"),
        signature_header=request.headers.get("X-Slack-Signature"),
    )

    if not valid:
        # Don't leak why verification failed — same 401 whether the
        # secret was missing, the timestamp was stale, or the HMAC mismatched.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Slack signature",
        )

    # Slack sends interactive payloads as
    # application/x-www-form-urlencoded with a single "payload" field
    # containing JSON — not as JSON body directly.
    form = parse_qs(raw_body.decode("utf-8"))
    payload_raw = form.get("payload", [None])[0]

    if payload_raw is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Slack payload",
        )

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed Slack payload",
        )

    actions = payload.get("actions", [])

    if not actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No action in Slack payload",
        )

    action = actions[0]
    action_id = action.get("action_id")
    incident_id_raw = action.get("value")
    slack_user = payload.get("user", {})
    # Readable name in the audit log; fall back to the immutable user id.
    slack_user_label = (
        slack_user.get("username")
        or slack_user.get("name")
        or slack_user.get("id", "unknown")
    )
    actioned_by = f"slack:{slack_user_label}"
    response_url = payload.get("response_url")

    try:
        incident_id = int(incident_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid incident id in Slack payload",
        )

    if action_id not in ("approve_incident", "reject_incident"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown Slack action_id: {action_id}",
        )

    try:
        if action_id == "approve_incident":
            incident, _approval, _action = approval_service.approve_incident(
                db, incident_id, actioned_by
            )
            result_text = (
                f"Incident #{incident_id} approved and remediated by {actioned_by}."
            )
            outcome = f":white_check_mark: *Approved* by {actioned_by} — remediation executed."
            logger.info(
                "slack_action_approved",
                incident_id=incident_id,
                actioned_by=actioned_by,
            )
        else:
            incident, _approval = approval_service.reject_incident(
                db, incident_id, actioned_by, DEFAULT_SLACK_REJECTION_REASON
            )
            result_text = f"Incident #{incident_id} rejected by {actioned_by}."
            outcome = f":no_entry: *Rejected* by {actioned_by}."
            logger.info(
                "slack_action_rejected",
                incident_id=incident_id,
                actioned_by=actioned_by,
            )
    except HTTPException as exc:
        if exc.status_code != status.HTTP_409_CONFLICT:
            raise
        # Someone (Slack or dashboard) already decided. Tell only the person
        # who clicked, instead of showing Slack an error icon.
        background_tasks.add_task(
            slack_service.update_via_response_url,
            response_url,
            {
                "response_type": "ephemeral",
                "replace_original": False,
                "text": f":warning: {exc.detail}",
            },
        )
        return {"text": str(exc.detail)}

    # Blocks are built here, before the response goes out: the DB session
    # is closed by the time a background task runs.
    background_tasks.add_task(
        slack_service.update_via_response_url,
        response_url,
        {
            "replace_original": True,
            "text": result_text,
            "blocks": slack_service.build_outcome_blocks(incident, outcome),
        },
    )
    return {"text": result_text}