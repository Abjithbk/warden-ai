"""
Service layer for incidents — pure functions over a DB session, no FastAPI
imports here. Keeps routers thin and makes this layer easy to unit test.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.models.incident import Incident


def list_incidents(
    db: Session,
    *,
    status: IncidentStatus | None = None,
    severity: IncidentSeverity | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Incident], int]:
    """Returns (page of incidents, total matching count) newest first."""
    query = select(Incident)
    count_query = select(func.count()).select_from(Incident)

    if status is not None:
        query = query.where(Incident.status == status)
        count_query = count_query.where(Incident.status == status)
    if severity is not None:
        query = query.where(Incident.severity == severity)
        count_query = count_query.where(Incident.severity == severity)

    total = db.execute(count_query).scalar_one()

    query = query.order_by(Incident.created_at.desc()).limit(limit).offset(offset)
    items = list(db.execute(query).scalars().all())

    return items, total
