import csv
import io
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import AuditLogEntry

MAX_EXPORT_ROWS = 10_000
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _filters(incident_id: int | None, actor: str | None, action: str | None) -> list:
    conds = []
    if incident_id is not None:
        conds.append(AuditLogEntry.incident_id == incident_id)
    if actor is not None:
        conds.append(AuditLogEntry.actor == actor)
    if action is not None:
        conds.append(AuditLogEntry.action == action)
    return conds


def _order():
    return (AuditLogEntry.created_at.desc(), AuditLogEntry.id.desc())


def list_audit_entries(
    db: Session, *, incident_id=None, actor=None, action=None, limit=50, offset=0
) -> tuple[list[AuditLogEntry], int]:
    conds = _filters(incident_id, actor, action)
    total = db.execute(
        select(func.count()).select_from(AuditLogEntry).where(*conds)
    ).scalar_one()
    items = db.execute(
        select(AuditLogEntry).where(*conds).order_by(*_order()).limit(limit).offset(offset)
    ).scalars().all()
    return list(items), total


def _safe_cell(value: object) -> str:
    """Neutralise CSV/Excel formula injection."""
    text = str(value)
    return f"'{text}" if text.startswith(_FORMULA_PREFIXES) else text


def export_audit_csv(db: Session, *, incident_id=None, actor=None, action=None) -> str:
    entries = db.execute(
        select(AuditLogEntry)
        .where(*_filters(incident_id, actor, action))
        .order_by(*_order())
        .limit(MAX_EXPORT_ROWS)
    ).scalars().all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "incident_id", "actor", "action", "detail", "created_at"])
    for e in entries:
        w.writerow([
            e.id, e.incident_id, _safe_cell(e.actor), _safe_cell(e.action),
            _safe_cell(json.dumps(e.detail, default=str, sort_keys=True)),
            e.created_at.isoformat(),
        ])
    return buf.getvalue()