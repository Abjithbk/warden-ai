from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from backend.core.errors import NotFoundError
from backend.core.limiter import limiter
from backend.db.session import get_db
from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.schemas.approval import (
    ApprovalActionResponse,
    ApproveRequest,
    RejectRequest,
)
from backend.schemas.incident import IncidentDetailOut, IncidentListOut
from backend.services import approval_service, incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListOut)
def get_incidents(
    status: IncidentStatus | None = Query(default=None),
    severity: IncidentSeverity | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IncidentListOut:
    items, total = incident_service.list_incidents(
        db, status=status, severity=severity, limit=limit, offset=offset
    )
    return IncidentListOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/{incident_id}", response_model=IncidentDetailOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)) -> IncidentDetailOut:
    incident = incident_service.get_incident_detail(db, incident_id)
    if incident is None:
        raise NotFoundError("Incident not found")
    return IncidentDetailOut.model_validate(incident)


@router.post("/{incident_id}/approve", response_model=ApprovalActionResponse)
@limiter.limit("10/minute")
def approve(
    request: Request, incident_id: int, body: ApproveRequest, db: Session = Depends(get_db)
) -> ApprovalActionResponse:
    incident, approval, action = approval_service.approve_incident(
        db, incident_id, body.actioned_by
    )
    return ApprovalActionResponse(
        incident_id=incident.id,
        incident_status=incident.status,
        approval_request_id=approval.id,
        approval_status=approval.status,
        actioned_by=approval.actioned_by,
        actioned_at=approval.actioned_at,
        remediation_action=action,
    )


@router.post("/{incident_id}/reject", response_model=ApprovalActionResponse)
@limiter.limit("10/minute")
def reject(
    request: Request, incident_id: int, body: RejectRequest, db: Session = Depends(get_db)
) -> ApprovalActionResponse:
    incident, approval = approval_service.reject_incident(
        db, incident_id, body.actioned_by, body.reason
    )
    return ApprovalActionResponse(
        incident_id=incident.id,
        incident_status=incident.status,
        approval_request_id=approval.id,
        approval_status=approval.status,
        actioned_by=approval.actioned_by,
        actioned_at=approval.actioned_at,
        rejection_reason=approval.rejection_reason,
    )