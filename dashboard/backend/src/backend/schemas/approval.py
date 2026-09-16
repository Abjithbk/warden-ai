"""
Request/response schemas for the approve/reject endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from backend.models.enums import ActionStatus, ActionType, ApprovalStatus, IncidentStatus


class ApproveRequest(BaseModel):
    # No auth system yet — caller identifies itself. Slack handler will pass
    # "slack:<user_id>", dashboard will pass "dashboard:<username>".
    actioned_by: str = Field(default="dashboard:unknown", max_length=255)


class RejectRequest(BaseModel):
    actioned_by: str = Field(default="dashboard:unknown", max_length=255)
    reason: str = Field(min_length=1, max_length=2000)


class RemediationActionOut(BaseModel):
    id: int
    action_type: ActionType
    target: str
    status: ActionStatus
    result: dict | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ApprovalActionResponse(BaseModel):
    incident_id: int
    incident_status: IncidentStatus
    approval_request_id: int
    approval_status: ApprovalStatus
    actioned_by: str
    actioned_at: datetime
    rejection_reason: str | None = None
    remediation_action: RemediationActionOut | None = None

    model_config = {"from_attributes": True}
