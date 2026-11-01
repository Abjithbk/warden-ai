"""Human approval gate: approve_incident / reject_incident.

Both lock the latest ApprovalRequest row (FOR UPDATE) so a Slack click and a
dashboard click cannot both succeed; the loser gets a 409.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.core.errors import ConflictError, PolicyDeniedError
from backend.models import (
    ActionStatus,
    ApprovalRequest,
    ApprovalStatus,
    AuditLogEntry,
    Incident,
    IncidentStatus,
    PolicyVerdict,
    RemediationAction,
)
from backend.services._common import (
    commit_or_rollback,
    get_incident_or_404,
    get_latest_approval,
    get_policy_and_decision,
)


def _assert_actionable(incident: Incident, approval: ApprovalRequest) -> None:
    if approval.actioned_at is not None or approval.status != ApprovalStatus.pending:
        when = approval.actioned_at.isoformat() if approval.actioned_at else "earlier"
        raise ConflictError(
            f"Approval request already {approval.status.value} "
            f"at {when} by {approval.actioned_by or 'unknown'}"
        )
    if incident.status != IncidentStatus.awaiting_approval:
        raise ConflictError(
            f"Incident is not awaiting approval (status: {incident.status.value})"
        )


def _audit(db: Session, incident_id: int, actor: str, action: str, detail: dict) -> None:
    db.add(AuditLogEntry(incident_id=incident_id, actor=actor, action=action, detail=detail))


def _run_stub_execution(db, incident, approval, decision) -> RemediationAction:
    """STUB for the M7 executor. Replace the body only; callers stay the same.
    The real flow should leave the incident `remediating` and let the rollback
    monitor mark it `resolved` after verification."""
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


def approve_incident(
    db: Session, incident_id: int, actioned_by: str
) -> tuple[Incident, ApprovalRequest, RemediationAction]:
    incident = get_incident_or_404(db, incident_id)
    approval = get_latest_approval(db, incident_id, lock=True)
    _assert_actionable(incident, approval)

    policy, decision = get_policy_and_decision(db, approval.policy_check_id)
    if policy.verdict != PolicyVerdict.approved:  # guardrail must never be bypassable
        raise PolicyDeniedError(f"Policy '{policy.policy_name}' denied this action")

    now = datetime.now(UTC)
    approval.status = ApprovalStatus.approved
    approval.actioned_by = actioned_by
    approval.actioned_at = now

    action = _run_stub_execution(db, incident, approval, decision)
    incident.status = IncidentStatus.resolved
    incident.resolved_at = action.completed_at

    _audit(db, incident_id, actioned_by, "approval_approved",
           {"approval_request_id": approval.id})
    _audit(db, incident_id, "executor", "action_succeeded",
           {"action_type": action.action_type.value, "target": action.target})

    commit_or_rollback(db)
    db.refresh(incident)
    db.refresh(approval)
    db.refresh(action)
    return incident, approval, action


def reject_incident(
    db: Session, incident_id: int, actioned_by: str, reason: str
) -> tuple[Incident, ApprovalRequest]:
    incident = get_incident_or_404(db, incident_id)
    approval = get_latest_approval(db, incident_id, lock=True)
    _assert_actionable(incident, approval)

    approval.status = ApprovalStatus.rejected
    approval.actioned_by = actioned_by
    approval.actioned_at = datetime.now(UTC)
    approval.rejection_reason = reason
    incident.status = IncidentStatus.rejected

    _audit(db, incident_id, actioned_by, "approval_rejected",
           {"approval_request_id": approval.id, "reason": reason})

    commit_or_rollback(db)
    db.refresh(incident)
    db.refresh(approval)
    return incident, approval