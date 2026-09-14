"""
Seeds the database with realistic incidents, plus every linked record an
incident touches on its way through the pipeline (Detection -> AgentDecision
-> PolicyCheck -> ApprovalRequest -> RemediationAction -> AuditLogEntry).

Run with:
    uv run python scripts/seed.py

Safe to re-run: it wipes and recreates all rows in the tables it seeds
(does NOT drop/recreate the schema — run `alembic upgrade head` first).
"""

import random
from datetime import UTC, datetime, timedelta

from faker import Faker

from backend.db.session import SessionLocal
from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.audit_log_entry import AuditLogEntry
from backend.models.detection import Detection
from backend.models.enums import (
    ActionStatus,
    ActionType,
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    PolicyVerdict,
)
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck
from backend.models.remediation_action import RemediationAction

fake = Faker()

SERVICES = ["checkout", "payments-api", "auth-service", "inventory", "notifications", "search"]
NAMESPACES = ["prod", "prod-eu", "staging"]
SIGNAL_SOURCES = ["prometheus", "k8s-events", "otel-traces"]
SIGNALS = ["OOMKilled", "HighLatency", "CrashLoopBackOff", "ErrorRateSpike", "PodPending"]

# Roughly mirrors the dashboard mockup: a handful of active/awaiting
# incidents, most of the rest resolved.
SEED_PLAN = [
    (IncidentStatus.active, IncidentSeverity.critical),
    (IncidentStatus.active, IncidentSeverity.high),
    (IncidentStatus.awaiting_approval, IncidentSeverity.high),
    (IncidentStatus.remediating, IncidentSeverity.medium),
    (IncidentStatus.resolved, IncidentSeverity.critical),
    (IncidentStatus.resolved, IncidentSeverity.high),
    (IncidentStatus.resolved, IncidentSeverity.high),
    (IncidentStatus.resolved, IncidentSeverity.medium),
    (IncidentStatus.resolved, IncidentSeverity.medium),
    (IncidentStatus.resolved, IncidentSeverity.low),
    (IncidentStatus.resolved, IncidentSeverity.low),
    (IncidentStatus.rejected, IncidentSeverity.low),
]


def utcnow() -> datetime:
    return datetime.now(UTC)


def wipe_existing(db) -> None:
    """Delete children first, then incidents, respecting FK order."""
    db.query(AuditLogEntry).delete()
    db.query(RemediationAction).delete()
    db.query(ApprovalRequest).delete()
    db.query(PolicyCheck).delete()
    db.query(AgentDecision).delete()
    db.query(Detection).delete()
    db.query(Incident).delete()
    db.commit()


def build_incident(status: IncidentStatus, severity: IncidentSeverity, index: int) -> Incident:
    service = random.choice(SERVICES)
    signal = random.choice(SIGNALS)
    created_at = utcnow() - timedelta(hours=random.randint(1, 96), minutes=random.randint(0, 59))

    incident = Incident(
        title=f"{signal.replace('_', ' ')} on {service}",
        service=service,
        namespace=random.choice(NAMESPACES),
        severity=severity,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )
    return incident


def attach_pipeline(db, incident: Incident, status: IncidentStatus, index: int) -> None:
    """Builds the Detection -> ... -> AuditLogEntry chain appropriate for
    this incident's status, keeping timestamps monotonically increasing."""
    t = incident.created_at

    def add_audit(actor: str, action: str, detail: dict, at: datetime) -> None:
        db.add(
            AuditLogEntry(
                incident_id=incident.id,
                actor=actor,
                action=action,
                detail=detail,
                created_at=at,
                updated_at=at,
            )
        )

    detection = Detection(
        incident_id=incident.id,
        source=random.choice(SIGNAL_SOURCES),
        signal=incident.title.split(" on ")[0].replace(" ", ""),
        raw_payload={"pod": f"{incident.service}-{fake.uuid4()[:8]}", "namespace": incident.namespace},
        created_at=t,
        updated_at=t,
    )
    db.add(detection)
    add_audit("system", "incident_created", {"source": detection.source, "signal": detection.signal}, t)

    # `active` incidents stop right after detection - nothing has reasoned
    # about them yet.
    if status == IncidentStatus.active:
        return

    t += timedelta(seconds=random.randint(5, 30))
    action_type = random.choice(list(ActionType))
    decision = AgentDecision(
        incident_id=incident.id,
        reasoning_trace=[
            {"step": "analyze_signals", "output": f"Correlated {detection.signal} with recent deploy."},
            {"step": "propose_fix", "output": f"Recommending {action_type.value} on {incident.service}."},
        ],
        proposed_action=action_type,
        target=f"{incident.service}-deployment",
        confidence=round(random.uniform(0.6, 0.98), 2),
        created_at=t,
        updated_at=t,
    )
    db.add(decision)
    db.flush()  # assigns decision.id - PolicyCheck needs it as a plain FK (no ORM relationship exists)
    add_audit(
        "agent",
        "decision_proposed",
        {"proposed_action": action_type.value, "confidence": decision.confidence},
        t,
    )

    t += timedelta(seconds=random.randint(1, 5))
    # Rejected incidents got a `denied` policy verdict and stop there.
    verdict = PolicyVerdict.denied if status == IncidentStatus.rejected else PolicyVerdict.approved
    policy_check = PolicyCheck(
        incident_id=incident.id,
        agent_decision_id=decision.id,
        verdict=verdict,
        reason=(
            "Blocked: action targets a protected namespace."
            if verdict == PolicyVerdict.denied
            else "Within guardrails: replica count and namespace checks passed."
        ),
        policy_name="min_replica_count" if verdict == PolicyVerdict.denied else "standard_remediation",
        created_at=t,
        updated_at=t,
    )
    db.add(policy_check)
    db.flush()  # assigns policy_check.id - ApprovalRequest needs it as a plain FK
    add_audit("policy-engine", f"policy_{verdict.value}", {"policy_name": policy_check.policy_name}, t)

    if status == IncidentStatus.rejected:
        return

    t += timedelta(seconds=random.randint(10, 120))
    approval_status = {
        IncidentStatus.awaiting_approval: ApprovalStatus.pending,
        IncidentStatus.remediating: ApprovalStatus.approved,
        IncidentStatus.resolved: ApprovalStatus.approved,
    }[status]
    actioned_by = "slack:U0123ABC" if index % 2 == 0 else "dashboard:amaya"
    approval = ApprovalRequest(
        incident_id=incident.id,
        policy_check_id=policy_check.id,
        status=approval_status,
        actioned_by=actioned_by if approval_status != ApprovalStatus.pending else None,
        actioned_at=t if approval_status != ApprovalStatus.pending else None,
        created_at=t,
        updated_at=t,
    )
    db.add(approval)
    db.flush()  # assigns approval.id - RemediationAction needs it as a plain FK
    add_audit(
        actioned_by if approval_status != ApprovalStatus.pending else "system",
        "approval_requested",
        {"policy_check_id": policy_check.id},
        t,
    )

    if status == IncidentStatus.awaiting_approval:
        return

    t += timedelta(seconds=random.randint(5, 20))
    action_status = ActionStatus.in_progress if status == IncidentStatus.remediating else ActionStatus.succeeded
    completed_at = t + timedelta(seconds=random.randint(10, 60)) if action_status == ActionStatus.succeeded else None
    action = RemediationAction(
        incident_id=incident.id,
        approval_request_id=approval.id,
        action_type=decision.proposed_action,
        target=decision.target,
        status=action_status,
        result={"message": "restart succeeded"} if action_status == ActionStatus.succeeded else None,
        started_at=t,
        completed_at=completed_at,
        created_at=t,
        updated_at=t,
    )
    db.add(action)
    add_audit(
        "executor",
        f"action_{action_status.value}",
        {"action_type": action.action_type.value, "target": action.target},
        t,
    )

    if status == IncidentStatus.resolved:
        incident.resolved_at = completed_at
        incident.updated_at = completed_at


def main() -> None:
    db = SessionLocal()
    try:
        wipe_existing(db)

        for index, (status, severity) in enumerate(SEED_PLAN):
            incident = build_incident(status, severity, index)
            db.add(incident)
            db.flush()  # assigns incident.id, needed for relationships below
            attach_pipeline(db, incident, status, index)

        db.commit()
        print(f"Seeded {len(SEED_PLAN)} incidents with full pipeline records.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
