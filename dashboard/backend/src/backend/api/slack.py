
"""
Slack interactivity webhook — approve/reject buttons on the incident
notification message call back here. Reuses approval_service directly so
Slack and the dashboard go through the exact same idempotency-guarded logic.
"""

import json
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.logging import logger
from backend.db.session import get_db
from backend.security.slack import is_valid_slack_signature
from backend.services import approval_service

router = APIRouter(prefix="/slack", tags=["slack"])

DEFAULT_SLACK_REJECTION_REASON = "Rejected via Slack"


@router.post("/actions")
async def slack_actions(request: Request, db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    raw_body = await request.body()

    valid = is_valid_slack_signature(
        signing_secret=settings.slack_signing_secret,
        request_body=raw_body,
        timestamp_header=request.headers.get("X-Slack-Request-Timestamp"),
        signature_header=request.headers.get("X-Slack-Signature"),
    )
    if not valid:
        # Don't leak *why* verification failed — same 401 whether the
        # secret was missing, the timestamp was stale, or the HMAC mismatched.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Slack signature")

    # Slack sends interactive payloads as
    # application/x-www-form-urlencoded with a single "payload" field
    # containing JSON — not as JSON body directly.
    form = parse_qs(raw_body.decode("utf-8"))
    payload_raw = form.get("payload", [None])[0]
    if payload_raw is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Slack payload")

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed Slack payload")

    actions = payload.get("actions", [])
    if not actions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No action in Slack payload")

    action = actions[0]
    action_id = action.get("action_id")
    incident_id_raw = action.get("value")
    slack_user_id = payload.get("user", {}).get("id", "unknown")
    actioned_by = f"slack:{slack_user_id}"

    try:
        incident_id = int(incident_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id in Slack payload")

    if action_id == "approve_incident":
        incident, approval, remediation_action = approval_service.approve_incident(db, incident_id, actioned_by)
        logger.info("slack_action_approved", incident_id=incident_id, actioned_by=actioned_by)
        return {"text": f"Incident #{incident_id} approved and remediated by {actioned_by}."}

    if action_id == "reject_incident":
        incident, approval = approval_service.reject_incident(
            db, incident_id, actioned_by, DEFAULT_SLACK_REJECTION_REASON
        )
        logger.info("slack_action_rejected", incident_id=incident_id, actioned_by=actioned_by)
        return {"text": f"Incident #{incident_id} rejected by {actioned_by}."}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown Slack action_id: {action_id}")