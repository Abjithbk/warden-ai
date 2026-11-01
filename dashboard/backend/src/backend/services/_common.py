from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.errors import NotFoundError
from backend.models import AgentDecision, ApprovalRequest, Incident, PolicyCheck


def get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise NotFoundError("Incident not found")
    return incident


def get_latest_approval(
    db: Session, incident_id: int, *, lock: bool = False
) -> ApprovalRequest:
    """Single definition of 'the current approval' for approve/reject/notify."""
    stmt = (
        select(ApprovalRequest)
        .where(ApprovalRequest.incident_id == incident_id)
        .order_by(ApprovalRequest.created_at.desc(), ApprovalRequest.id.desc())
        .limit(1)
    )
    if lock:
        stmt = stmt.with_for_update()  # no-op on SQLite
    approval = db.execute(stmt).scalar_one_or_none()
    if approval is None:
        raise NotFoundError("No approval request exists for this incident")
    return approval


def get_policy_and_decision(
    db: Session, policy_check_id: int
) -> tuple[PolicyCheck, AgentDecision]:
    row = db.execute(
        select(PolicyCheck, AgentDecision)
        .join(AgentDecision, AgentDecision.id == PolicyCheck.agent_decision_id)
        .where(PolicyCheck.id == policy_check_id)
    ).one_or_none()
    if row is None:
        raise NotFoundError("No agent decision found behind this approval request")
    return row[0], row[1]


def commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise