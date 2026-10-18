"""
Outbound Slack: post the approval request (with Approve/Reject buttons),
send a test message, and update the original message after a click.

Inbound clicks are handled in api/slack.py (signature-verified) and go
through approval_service, so Slack and the dashboard share one code path.

Uses only the stdlib for HTTP so no new dependency is needed. All network
access goes through _post_json — tests monkeypatch that one function.
"""

import json
import urllib.error
import urllib.request
import http.client
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.logging import logger
from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.audit_log_entry import AuditLogEntry
from backend.models.enums import ApprovalStatus
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck

SLACK_TIMEOUT_SECONDS = 5.0
# response_url values come from a signed Slack payload, but we still refuse
# to POST anywhere except Slack (defence in depth against SSRF).
ALLOWED_RESPONSE_URL_PREFIX = "https://hooks.slack.com/"


class SlackError(Exception):
    """Network failure or Slack API returned ok=false."""


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def _post_json(url: str, payload: dict[str, Any], token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=SLACK_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        # Must come before URLError (HTTPError is a subclass). Keep Slack's
        # reply body: it says why (e.g. expired response_url, rate limit).
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        raise SlackError(f"Slack HTTP {exc.code}: {detail}") from exc
    except (OSError, http.client.HTTPException, ValueError) as exc:
        # OSError covers URLError, timeouts, RemoteDisconnected, resets;
        # ValueError covers a bad URL or an undecodable body.
        raise SlackError(f"Slack unreachable: {exc}") from exc


def _call_api(method: str, payload: dict[str, Any]) -> dict:
    settings = get_settings()
    data = _post_json(
        f"{settings.slack_api_base_url}/{method}",
        payload,
        token=settings.slack_bot_token,
    )
    if not data.get("ok"):
        raise SlackError(data.get("error", "unknown_error"))
    return data


# --------------------------------------------------------------------------
# Status
# --------------------------------------------------------------------------
def can_notify() -> bool:
    settings = get_settings()
    return bool(settings.slack_bot_token and settings.slack_channel_id)


def get_status() -> dict[str, Any]:
    settings = get_settings()
    return {
        "can_notify": can_notify(),
        "can_receive_actions": bool(settings.slack_signing_secret),
        "bot_token_set": bool(settings.slack_bot_token),
        "signing_secret_set": bool(settings.slack_signing_secret),
        "channel_id": settings.slack_channel_id or None,
    }


def _require_configured() -> None:
    if not can_notify():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Slack is not configured (set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID)",
        )


def _slack_failure(exc: SlackError) -> HTTPException:
    logger.warning("slack_api_failed", error=str(exc))
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Slack request failed: {exc}",
    )


# --------------------------------------------------------------------------
# Block Kit builders (pure functions — easy to test)
# --------------------------------------------------------------------------
def _esc(text: str) -> str:
    """Escape the three characters Slack mrkdwn treats as control chars."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _header_blocks(incident: Incident) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":rotating_light: *{incident.severity.value.upper()}* · "
                    f"Incident #{incident.id}\n*{_esc(incident.title)}*"
                ),
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Service*\n{_esc(incident.service)}"},
                {"type": "mrkdwn", "text": f"*Namespace*\n{_esc(incident.namespace)}"},
            ],
        },
    ]


def _link_block(incident_id: int) -> dict:
    base = get_settings().dashboard_base_url.rstrip("/")
    return {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"<{base}/incidents/{incident_id}|Open in Warden>",
            }
        ],
    }


def build_approval_blocks(incident: Incident, decision: AgentDecision) -> list[dict]:
    blocks = _header_blocks(incident)
    blocks.append(
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Proposed action*\n`{decision.proposed_action.value}`",
                },
                {"type": "mrkdwn", "text": f"*Target*\n{_esc(decision.target)}"},
                {"type": "mrkdwn", "text": f"*Confidence*\n{decision.confidence:.0%}"},
            ],
        }
    )
    blocks.append(
        {
            "type": "actions",
            "block_id": f"approval_{incident.id}",
            "elements": [
                {
                    "type": "button",
                    "action_id": "approve_incident",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": str(incident.id),
                    "confirm": {
                        "title": {"type": "plain_text", "text": "Run this action?"},
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"`{decision.proposed_action.value}` will run on "
                                f"*{_esc(decision.target)}* in production."
                            ),
                        },
                        "confirm": {"type": "plain_text", "text": "Approve"},
                        "deny": {"type": "plain_text", "text": "Cancel"},
                    },
                },
                {
                    "type": "button",
                    "action_id": "reject_incident",
                    "text": {"type": "plain_text", "text": "Reject"},
                    "style": "danger",
                    "value": str(incident.id),
                },
            ],
        }
    )
    blocks.append(_link_block(incident.id))
    return blocks


def build_outcome_blocks(incident: Incident, outcome_text: str) -> list[dict]:
    """Same header, buttons replaced by the outcome — stops repeat clicks."""
    blocks = _header_blocks(incident)
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": outcome_text}})
    blocks.append(_link_block(incident.id))
    return blocks


# --------------------------------------------------------------------------
# Outbound actions
# --------------------------------------------------------------------------
def _latest_approval(
    db: Session, incident_id: int, *, lock: bool = False
) -> ApprovalRequest:
    query = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.incident_id == incident_id)
        .order_by(ApprovalRequest.created_at.desc(), ApprovalRequest.id.desc())
    )
    if lock:
        # Row lock (same pattern as approval_service): two concurrent notify
        # requests serialize here, so the second sees slack_message_ts and
        # does not post a duplicate. No-op on SQLite.
        query = query.with_for_update()
    approval = query.first()
    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approval request exists for this incident",
        )
    return approval


def notify_approval_requested(
    db: Session, incident_id: int, *, force: bool = False
) -> tuple[ApprovalRequest, bool]:
    """
    Post the approval request to Slack. Returns (approval, already_sent).

    Call this from the agent/policy pipeline right after the ApprovalRequest
    row is created (wrap in try/except HTTPException — a Slack outage must
    not break incident handling; the dashboard still works).
    """
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )
    approval = _latest_approval(db, incident_id,lock=True)

    if approval.status != ApprovalStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval request is not pending (current status: {approval.status.value})",
        )
    if approval.slack_message_ts and not force:
        return approval, True

    _require_configured()

    decision = (
        db.query(AgentDecision)
        .join(PolicyCheck, PolicyCheck.agent_decision_id == AgentDecision.id)
        .filter(PolicyCheck.id == approval.policy_check_id)
        .first()
    )
    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No agent decision found behind this approval request",
        )

    settings = get_settings()
    try:
        data = _call_api(
            "chat.postMessage",
            {
                "channel": settings.slack_channel_id,
                # plain-text fallback for push notifications / screen readers
                "text": (
                    f"Approval needed: {incident.title} "
                    f"({decision.proposed_action.value} on {decision.target})"
                ),
                "blocks": build_approval_blocks(incident, decision),
            },
        )
    except SlackError as exc:
        raise _slack_failure(exc) from exc

    approval.slack_channel = data.get("channel", settings.slack_channel_id)
    approval.slack_message_ts = data.get("ts")
    db.add(
        AuditLogEntry(
            incident_id=incident_id,
            actor="system",
            action="slack_notified",
            detail={
                "service": incident.service,
                "channel": approval.slack_channel,
                "ts": approval.slack_message_ts,
                "approval_request_id": approval.id,
            },
        )
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(approval)
    return approval, False


def send_test_message() -> dict[str, str]:
    _require_configured()
    settings = get_settings()
    try:
        data = _call_api(
            "chat.postMessage",
            {
                "channel": settings.slack_channel_id,
                "text": ":white_check_mark: Warden test message — Slack is connected.",
            },
        )
    except SlackError as exc:
        raise _slack_failure(exc) from exc
    return {
        "channel": data.get("channel", settings.slack_channel_id),
        "ts": data.get("ts", ""),
    }


def update_via_response_url(response_url: str | None, payload: dict[str, Any]) -> None:
    """
    Replace (or reply to) the Slack message that was clicked. Runs as a
    background task AFTER Warden has already answered Slack, so it must
    never raise and never touch the DB session.
    """
    if not response_url or not response_url.startswith(ALLOWED_RESPONSE_URL_PREFIX):
        logger.warning("slack_response_url_rejected")
        return
    try:
        _post_json(response_url, payload)
    except SlackError as exc:
        logger.warning("slack_response_url_failed", error=str(exc))