"""
Pydantic schemas for Incident list and detail API responses.
Combines list items and the full pipeline trace (Detection -> RemediationAction).
"""

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from backend.models.enums import (
    ActionStatus,
    ActionType,
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    PolicyVerdict,
)

# --- Nested child trace schemas ---

class DetectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    signal: str
    raw_payload: dict[str, Any]
    created_at: datetime


class AgentDecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reasoning_trace: list[dict[str, Any]]
    proposed_action: ActionType
    target: str
    confidence: float
    created_at: datetime


class PolicyCheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_decision_id: int
    verdict: PolicyVerdict
    reason: str
    policy_name: str | None
    created_at: datetime


class ApprovalRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_check_id: int
    status: ApprovalStatus
    actioned_by: str | None
    actioned_at: datetime | None
    rejection_reason: str | None
    slack_channel: str | None = None
    slack_message_ts: str | None = None
    created_at: datetime


class RemediationActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    approval_request_id: int
    action_type: ActionType
    target: str
    status: ActionStatus
    result: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class AuditLogEntryBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    detail: dict[str, Any]
    created_at: datetime


# --- Main Incident schemas ---

class IncidentOut(BaseModel):
    """Shape returned for each incident in list/feed endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    service: str
    namespace: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None


class IncidentListOut(BaseModel):
    """Paginated wrapper around a list of incidents."""
    items: list[IncidentOut]
    total: int
    limit: int
    offset: int


class IncidentDetailOut(BaseModel):
    """Full detail trace for an incident."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    service: str
    namespace: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    detections: list[DetectionOut]
    agent_decisions: list[AgentDecisionOut]
    policy_checks: list[PolicyCheckOut]
    approval_requests: list[ApprovalRequestOut]
    remediation_actions: list[RemediationActionOut]
    audit_log: list[AuditLogEntryBriefOut] = Field(
        validation_alias = AliasChoices("audit_log","audit_log_entries")
    )


# Aliases for convenience
IncidentListItem = IncidentOut
IncidentDetail = IncidentDetailOut
