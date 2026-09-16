"""
Service layer for the human approval gate: approve_incident / reject_incident.

Both are idempotency-guarded on ApprovalRequest.actioned_at — this is the
field that blocks a Slack click and a dashboard click on the same request
from racing each other, per the model's own docstring.
"""

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.audit_log_entry import AuditLogEntry
from backend.models.enums import ActionStatus, ApprovalStatus, IncidentStatus
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck
from backend.models.remediation_action import RemediationAction


def _get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


def _get_pending_approval_or_404(db: Session, incident_id: int) -> ApprovalRequest:
    approval = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.incident_id == incident_id)
        .order_by(ApprovalRequest.created_at.desc())
        .first()
    )
    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approval request exists for this incident",
        )
    return approval


def _assert_not_already_actioned(approval: ApprovalRequest) -> None:
    # This is the race guard: Slack and dashboard both hit this. Whichever
    # transaction commits first wins; the second sees actioned_at set and
    # gets 409, not a silent double-action.
    if approval.actioned_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval request already {approval.status.value} at "
            f"{approval.actioned_at.isoformat()} by {approval.actioned_by}",
        )
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval request is not pending (current status: {approval.status.value})",
        )


def _run_stub_execution(db: Session, incident: Incident, approval: ApprovalRequest) -> RemediationAction:
    """
    STUB: simulates the executor module. Replace the body of this function
    with the real Kubernetes action call once the execution module lands —
    approve_incident() itself will not need to change.
    """
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

    now = datetime.now(UTC)
    action = RemediationAction(
        incident_id=incident.id,
        approval_request_id=approval.id,
        action_type=decision.proposed_action,
        target=decision.target,
        status=ActionStatus.succeeded,
        result={"message": "stub executor: action simulated successfully"},
        started_at=now,
        completed_at=now,
    )
    db.add(action)
    return action


def _add_audit(db: Session, incident_id: int, actor: str, action: str, detail: dict) -> None:
    db.add(
        AuditLogEntry(
            incident_id=incident_id,
            actor=actor,
            action=action,
            detail=detail,
        )
    )


def approve_incident(db: Session, incident_id: int, actioned_by: str) -> tuple[Incident, ApprovalRequest, RemediationAction]:
    incident = _get_incident_or_404(db, incident_id)
    approval = _get_pending_approval_or_404(db, incident_id)
    _assert_not_already_actioned(approval)

    now = datetime.now(UTC)
    approval.status = ApprovalStatus.approved
    approval.actioned_by = actioned_by
    approval.actioned_at = now

    action = _run_stub_execution(db, incident, approval)

    incident.status = IncidentStatus.resolved
    incident.resolved_at = action.completed_at
    incident.updated_at = now

    _add_audit(
        db,
        incident_id,
        actioned_by,
        "approval_approved",
        {"approval_request_id": approval.id},
    )
    _add_audit(
        db,
        incident_id,
        "executor",
        "action_succeeded",
        {"action_type": action.action_type.value, "target": action.target},
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(incident)
    db.refresh(approval)
    db.refresh(action)
    return incident, approval, action


def reject_incident(db: Session, incident_id: int, actioned_by: str, reason: str) -> tuple[Incident, ApprovalRequest]:
    incident = _get_incident_or_404(db, incident_id)
    approval = _get_pending_approval_or_404(db, incident_id)
    _assert_not_already_actioned(approval)

    now = datetime.now(UTC)
    approval.status = ApprovalStatus.rejected
    approval.actioned_by = actioned_by
    approval.actioned_at = now
    approval.rejection_reason = reason

    incident.status = IncidentStatus.rejected
    incident.updated_at = now

    _add_audit(
        db,
        incident_id,
        actioned_by,
        "approval_rejected",
        {"approval_request_id": approval.id, "reason": reason},
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(incident)
    db.refresh(approval)
    return incident, approval
