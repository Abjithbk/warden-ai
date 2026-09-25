
"""
Unit tests for approval_service — the idempotency guard and state
transitions, tested directly against the DB session (no HTTP, no rate
limiting involved at this layer).
"""

import pytest
from fastapi import HTTPException

from backend.models.enums import ActionStatus, ApprovalStatus, IncidentStatus
from backend.services import approval_service


def test_approve_incident_success(db_session, pending_incident):
    incident, _ = pending_incident

    updated_incident, updated_approval, action = approval_service.approve_incident(
        db_session, incident.id, "dashboard:amaya"
    )

    assert updated_approval.status == ApprovalStatus.approved
    assert updated_approval.actioned_by == "dashboard:amaya"
    assert updated_approval.actioned_at is not None
    assert updated_incident.status == IncidentStatus.resolved
    assert updated_incident.resolved_at is not None
    assert action.status == ActionStatus.succeeded


def test_approve_twice_returns_409(db_session, pending_incident):
    incident, _ = pending_incident
    approval_service.approve_incident(db_session, incident.id, "dashboard:amaya")

    with pytest.raises(HTTPException) as exc_info:
        approval_service.approve_incident(db_session, incident.id, "dashboard:amaya")

    assert exc_info.value.status_code == 409


def test_reject_incident_success(db_session, pending_incident):
    incident, _ = pending_incident

    updated_incident, updated_approval = approval_service.reject_incident(
        db_session, incident.id, "dashboard:amaya", "policy risk too high"
    )

    assert updated_approval.status == ApprovalStatus.rejected
    assert updated_approval.rejection_reason == "policy risk too high"
    assert updated_incident.status == IncidentStatus.rejected


def test_reject_then_approve_returns_409(db_session, pending_incident):
    incident, _ = pending_incident
    approval_service.reject_incident(db_session, incident.id, "dashboard:amaya", "too risky")

    with pytest.raises(HTTPException) as exc_info:
        approval_service.approve_incident(db_session, incident.id, "dashboard:amaya")

    assert exc_info.value.status_code == 409


def test_approve_nonexistent_incident_returns_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        approval_service.approve_incident(db_session, 9999, "dashboard:amaya")

    assert exc_info.value.status_code == 404


def test_approve_incident_with_no_pending_approval_returns_404(db_session):
    from backend.models.enums import IncidentSeverity
    from backend.models.incident import Incident

    incident = Incident(
        title="No pipeline yet",
        service="checkout",
        namespace="prod",
        severity=IncidentSeverity.low,
        status=IncidentStatus.active,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    with pytest.raises(HTTPException) as exc_info:
        approval_service.approve_incident(db_session, incident.id, "dashboard:amaya")

    assert exc_info.value.status_code == 404

