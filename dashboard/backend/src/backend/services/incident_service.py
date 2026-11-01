from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.models import Incident, IncidentSeverity, IncidentStatus


def list_incidents(
    db: Session,
    *,
    status: IncidentStatus | None = None,
    severity: IncidentSeverity | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Incident], int]:
    filters = []
    if status is not None:
        filters.append(Incident.status == status)
    if severity is not None:
        filters.append(Incident.severity == severity)

    total = db.execute(select(func.count()).select_from(Incident).where(*filters)).scalar_one()
    items = db.execute(
        select(Incident)
        .where(*filters)
        .order_by(Incident.created_at.desc(), Incident.id.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return list(items), total


def get_incident_detail(db: Session, incident_id: int) -> Incident | None:
    """Full pipeline in one round-trip; ordering comes from the relationships."""
    return db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .options(
            selectinload(Incident.detections),
            selectinload(Incident.agent_decisions),
            selectinload(Incident.policy_checks),
            selectinload(Incident.approval_requests),
            selectinload(Incident.remediation_actions),
            selectinload(Incident.audit_log_entries),
        )
    ).scalar_one_or_none()