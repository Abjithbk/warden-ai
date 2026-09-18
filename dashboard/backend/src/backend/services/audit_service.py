"""
Service layer for the audit trail — GET /api/v1/audit reads from
AuditLogEntry, the append-only table every pipeline stage writes to.
"""

import csv
import io

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.audit_log_entry import AuditLogEntry


def list_audit_entries(
    db: Session,
    *,
    incident_id: int | None = None,
    actor: str | None = None,
    action: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AuditLogEntry], int]:
    """Returns (page of entries, total matching count), newest first."""
    query = select(AuditLogEntry)
    count_query = select(func.count()).select_from(AuditLogEntry)

    if incident_id is not None:
        query = query.where(AuditLogEntry.incident_id == incident_id)
        count_query = count_query.where(AuditLogEntry.incident_id == incident_id)
    if actor is not None:
        query = query.where(AuditLogEntry.actor == actor)
        count_query = count_query.where(AuditLogEntry.actor == actor)
    if action is not None:
        query = query.where(AuditLogEntry.action == action)
        count_query = count_query.where(AuditLogEntry.action == action)

    total = db.execute(count_query).scalar_one()

    query = query.order_by(AuditLogEntry.created_at.desc()).limit(limit).offset(offset)
    items = list(db.execute(query).scalars().all())

    return items, total


def export_audit_csv(
    db: Session,
    *,
    incident_id: int | None = None,
    actor: str | None = None,
    action: str | None = None,
) -> str:
    """
    Same filters as list_audit_entries but no pagination — exports the full
    matching set as a CSV string. `detail` (a JSON dict) is flattened to its
    str() form since CSV has no nested-object concept.
    """
    query = select(AuditLogEntry)
    if incident_id is not None:
        query = query.where(AuditLogEntry.incident_id == incident_id)
    if actor is not None:
        query = query.where(AuditLogEntry.actor == actor)
    if action is not None:
        query = query.where(AuditLogEntry.action == action)
    query = query.order_by(AuditLogEntry.created_at.desc())

    entries = db.execute(query).scalars().all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "incident_id", "actor", "action", "detail", "created_at"])
    for entry in entries:
        writer.writerow(
            [entry.id, entry.incident_id, entry.actor, entry.action, str(entry.detail), entry.created_at.isoformat()]
        )

    return buffer.getvalue()