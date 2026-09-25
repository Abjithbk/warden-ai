
"""
Shared pytest fixtures: an isolated in-memory SQLite DB per test, a
TestClient wired to that DB via get_db override, and a pending_incident
fixture that builds a full Incident -> ... -> ApprovalRequest(pending)
chain so tests don't each hand-roll five model inserts.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db.base import Base
from backend.db.session import get_db
from backend.main import app
from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.detection import Detection
from backend.models.enums import (
    ActionType,
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    PolicyVerdict,
)
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # slowapi's default storage is in-memory and shared across the whole
    # process — reset before every test so each one starts with a clean
    # rate-limit budget instead of inheriting hits from an earlier test.
    from backend.core.limiter import limiter
    limiter.reset()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def pending_incident(db_session: Session) -> tuple[Incident, ApprovalRequest]:
    """Builds Incident(awaiting_approval) -> Detection -> AgentDecision ->
    PolicyCheck(approved) -> ApprovalRequest(pending). Returns (incident, approval).
    Available to any test in this directory just by naming it as a
    parameter — pytest injects it, no import required."""
    incident = Incident(
        title="OOMKilled on checkout",
        service="checkout",
        namespace="prod",
        severity=IncidentSeverity.high,
        status=IncidentStatus.awaiting_approval,
    )
    db_session.add(incident)
    db_session.flush()

    db_session.add(
        Detection(
            incident_id=incident.id,
            source="prometheus",
            signal="OOMKilled",
            raw_payload={"pod": "checkout-abc123"},
        )
    )

    decision = AgentDecision(
        incident_id=incident.id,
        reasoning_trace=[{"step": "analyze_logs", "output": "memory limit exceeded"}],
        proposed_action=ActionType.restart_pod,
        target="checkout-deployment",
        confidence=0.9,
    )
    db_session.add(decision)
    db_session.flush()

    policy_check = PolicyCheck(
        incident_id=incident.id,
        agent_decision_id=decision.id,
        verdict=PolicyVerdict.approved,
        reason="Within guardrails.",
        policy_name="standard_remediation",
    )
    db_session.add(policy_check)
    db_session.flush()

    approval = ApprovalRequest(
        incident_id=incident.id,
        policy_check_id=policy_check.id,
        status=ApprovalStatus.pending,
    )
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(incident)
    db_session.refresh(approval)

    return incident, approval
