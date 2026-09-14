from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.schemas.incident import IncidentListOut
from backend.services import incidents as incidents_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListOut)
def get_incidents(
    status: IncidentStatus | None = Query(default=None),
    severity: IncidentSeverity | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IncidentListOut:
    items, total = incidents_service.list_incidents(
        db, status=status, severity=severity, limit=limit, offset=offset
    )
    return IncidentListOut(items=items, total=total, limit=limit, offset=offset)
