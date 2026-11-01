"""
Service layer for the Overview page stats. Pure functions over a DB
session — no FastAPI imports, so this is easy to unit test directly.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import (
    ApprovalRequest,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    RemediationAction,
)
from backend.schemas.overview import OverviewStatsOut

# Points deducted from a perfect 100 sentinel score per active incident,
# scaled by severity. Purely a simple, explainable heuristic for now.
_SEVERITY_PENALTY = {
    IncidentSeverity.critical: 20,
    IncidentSeverity.high: 10,
    IncidentSeverity.medium: 5,
    IncidentSeverity.low: 2,
}

_ACTIVE_STATUSES = (
    IncidentStatus.active,
    IncidentStatus.awaiting_approval,
    IncidentStatus.remediating,
)


def compute_sentinel_score(db: Session) -> int:
    rows = db.execute(
        select(Incident.severity, func.count())
        .where(Incident.status.in_(_ACTIVE_STATUSES))
        .group_by(Incident.severity)
    ).all()
    penalty = sum(_SEVERITY_PENALTY.get(sev, 0) * n for sev, n in rows)
    return max(0, 100 - penalty)


def get_overview_stats(db: Session) -> OverviewStatsOut:
    return OverviewStatsOut(
        sentinel_score=compute_sentinel_score(db),
        active_incidents=count_active_incidents(db),
        auto_resolved_today=count_auto_resolved_today(db),
        avg_remediation_seconds=compute_avg_remediation_seconds(db),
        actions_last_24h=count_actions_last_24h(db),
    )
    
def count_active_incidents(db: Session) -> int:
    return db.execute(
        select(func.count())
        .select_from(Incident)
        .where(Incident.status.in_(_ACTIVE_STATUSES))
    ).scalar_one()


def count_auto_resolved_today(db: Session) -> int:
    start_of_today = datetime.now(UTC).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return db.execute(
        select(func.count())
        .select_from(Incident)
        .where(
            Incident.status == IncidentStatus.resolved,
            Incident.resolved_at.is_not(None),
            Incident.resolved_at >= start_of_today,
        )
    ).scalar_one()


def compute_avg_remediation_seconds(db: Session) -> float | None:
    """Average time from incident creation to resolution, across all resolved incidents."""
    rows = db.execute(
        select(Incident.created_at, Incident.resolved_at).where(
            Incident.status == IncidentStatus.resolved,
            Incident.resolved_at.is_not(None),
        )
    ).all()

    if not rows:
        return None

    durations = [
        (resolved_at - created_at).total_seconds() for created_at, resolved_at in rows
    ]
    return sum(durations) / len(durations)


def count_actions_last_24h(db: Session) -> int:
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    return db.execute(
        select(func.count())
        .select_from(RemediationAction)
        .where(RemediationAction.created_at >= cutoff)
    ).scalar_one()


def get_recent_actions(db: Session, *, limit: int = 10) -> list[dict]:
    """
    Last `limit` remediation actions, newest first, joined out to the
    incident title/service and the approver identity. actioned_by lives on
    ApprovalRequest, not RemediationAction, so this joins through
    approval_request_id rather than reading it off the action directly.
    """
    rows = db.execute(
        select(
            RemediationAction,
            Incident.title,
            Incident.service,
            ApprovalRequest.actioned_by,
        )
        .join(Incident, Incident.id == RemediationAction.incident_id)
        .join(
            ApprovalRequest, ApprovalRequest.id == RemediationAction.approval_request_id
        )
        .order_by(RemediationAction.created_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "id": action.id,
            "incident_id": action.incident_id,
            "incident_title": title,
            "service": service,
            "action_type": action.action_type,
            "target": action.target,
            "status": action.status,
            "actioned_by": actioned_by,
            "started_at": action.started_at,
            "completed_at": action.completed_at,
        }
        for action, title, service, actioned_by in rows
    ]
