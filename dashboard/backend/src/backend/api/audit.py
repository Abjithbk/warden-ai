
"""
Audit trail endpoints — the append-only record every pipeline stage writes
to, per REQ-7.x (Dashboard/Audit).
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from backend.db.session import get_db
from backend.schemas.audit import AuditLogListOut
from backend.services import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogListOut)
def get_audit_log(
    incident_id: int | None = Query(default=None),
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AuditLogListOut:
    items, total = audit_service.list_audit_entries(
        db, incident_id=incident_id, actor=actor, action=action, limit=limit, offset=offset
    )
    return AuditLogListOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/export")
def export_audit_log(
    incident_id: int | None = Query(default=None),
    actor: str | None = Query(default=None),
    action: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    csv_content = audit_service.export_audit_csv(db, incident_id=incident_id, actor=actor, action=action)
    filename = f"warden_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
