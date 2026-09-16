
"""
Service layer for incidents — pure functions over a DB session, no FastAPI
imports here. Keeps routers thin and makes this layer easy to unit test.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.audit_log_entry import AuditLogEntry
from backend.models.detection import Detection
from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck
from backend.models.remediation_action import RemediationAction


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


def get_incident_detail(db: Session, incident_id: int) -> dict | None:
    """
    Returns the full pipeline for one incident as a dict of ORM lists, or
    None if the incident doesn't exist. Walks incident_id on each child
    table directly — PolicyCheck/ApprovalRequest have no ORM relationship
    back to their parent, only plain FK columns, so this can't rely on
    nested relationship traversal from Incident down through the chain.
    """
    incident = db.get(Incident, incident_id)
    if incident is None:
        return None

    detections = (
        db.execute(
            select(Detection).where(Detection.incident_id == incident_id).order_by(Detection.created_at)
        )
        .scalars()
        .all()
    )
    agent_decisions = (
        db.execute(
            select(AgentDecision)
            .where(AgentDecision.incident_id == incident_id)
            .order_by(AgentDecision.created_at)
        )
        .scalars()
        .all()
    )
    policy_checks = (
        db.execute(
            select(PolicyCheck).where(PolicyCheck.incident_id == incident_id).order_by(PolicyCheck.created_at)
        )
        .scalars()
        .all()
    )
    approval_requests = (
        db.execute(
            select(ApprovalRequest)
            .where(ApprovalRequest.incident_id == incident_id)
            .order_by(ApprovalRequest.created_at)
        )
        .scalars()
        .all()
    )
    remediation_actions = (
        db.execute(
            select(RemediationAction)
            .where(RemediationAction.incident_id == incident_id)
            .order_by(RemediationAction.created_at)
        )
        .scalars()
        .all()
    )
    audit_log = (
        db.execute(
            select(AuditLogEntry).where(AuditLogEntry.incident_id == incident_id).order_by(AuditLogEntry.created_at)
        )
        .scalars()
        .all()
    )

    return {
        "incident": incident,
        "detections": list(detections),
        "agent_decisions": list(agent_decisions),
        "policy_checks": list(policy_checks),
        "approval_requests": list(approval_requests),
        "remediation_actions": list(remediation_actions),
        "audit_log": list(audit_log),
    }
