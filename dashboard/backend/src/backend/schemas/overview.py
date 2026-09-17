"""Pydantic schema for GET /api/v1/overview/stats."""

from pydantic import BaseModel
from datetime import datetime
from backend.models.enums import ActionStatus, ActionType


class OverviewStatsOut(BaseModel):
    sentinel_score: int
    active_incidents: int
    auto_resolved_today: int
    avg_remediation_seconds: float | None = None
    actions_last_24h: int

class RecentActionOut(BaseModel):
    id: int
    incident_id: int
    incident_title: str
    service: str
    action_type: ActionType
    target: str
    status: ActionStatus
    actioned_by: str | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}    
