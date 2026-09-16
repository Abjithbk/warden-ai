from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.approval import ApproveRequest, RejectRequest, ApprovalActionResponse
from backend.services import approval_service
from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.schemas.incident import IncidentListOut
from backend.services import incidents as incidents_service

from backend.schemas.incident_detail import IncidentDetailOut
from backend.services import incident_service

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


@router.post("/{incident_id}/approve", response_model=ApprovalActionResponse)
def approve(incident_id: int, body: ApproveRequest, db: Session = Depends(get_db)):
    incident, approval, action = approval_service.approve_incident(db, incident_id, body.actioned_by)
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
def reject(incident_id: int, body: RejectRequest, db: Session = Depends(get_db)):
    incident, approval = approval_service.reject_incident(db, incident_id, body.actioned_by, body.reason)
    return ApprovalActionResponse(
        incident_id=incident.id,
        incident_status=incident.status,
        approval_request_id=approval.id,
        approval_status=approval.status,
        actioned_by=approval.actioned_by,
        actioned_at=approval.actioned_at,
        rejection_reason=approval.rejection_reason,
    )  




@router.get("/{incident_id}", response_model=IncidentDetailOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    result = incident_service.get_incident_detail(db, incident_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = result["incident"]
    return IncidentDetailOut(
        id=incident.id,
        title=incident.title,
        service=incident.service,
        namespace=incident.namespace,
        severity=incident.severity,
        status=incident.status,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
        detections=result["detections"],
        agent_decisions=result["agent_decisions"],
        policy_checks=result["policy_checks"],
        approval_requests=result["approval_requests"],
        remediation_actions=result["remediation_actions"],
        audit_log=result["audit_log"],
    )      
