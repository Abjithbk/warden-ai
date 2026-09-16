"""
Response schema for GET /api/v1/incidents/{id} — full pipeline detail for
one incident: everything from Detection through AuditLogEntry.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from backend.models.enums import (
    ActionStatus,
    ActionType,
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    PolicyVerdict,
)


class DetectionOut(BaseModel):
    id: int
    source: str
    signal: str
    raw_payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentDecisionOut(BaseModel):
    id: int
    reasoning_trace: list[dict[str, Any]]
    proposed_action: ActionType
    target: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyCheckOut(BaseModel):
    id: int
    agent_decision_id: int
    verdict: PolicyVerdict
    reason: str
    policy_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequestOut(BaseModel):
    id: int
    policy_check_id: int
    status: ApprovalStatus
    actioned_by: str | None
    actioned_at: datetime | None
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RemediationActionOut(BaseModel):
    id: int
    approval_request_id: int
    action_type: ActionType
    target: str
    status: ActionStatus
    result: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AuditLogEntryOut(BaseModel):
    id: int
    actor: str
    action: str
    detail: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class IncidentDetailOut(BaseModel):
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
    audit_log: list[AuditLogEntryOut]