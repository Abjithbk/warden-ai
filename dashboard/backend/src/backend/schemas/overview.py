"""Pydantic schema for GET /api/v1/overview/stats."""

from pydantic import BaseModel


class OverviewStatsOut(BaseModel):
    sentinel_score: int
    active_incidents: int
    auto_resolved_today: int
    avg_remediation_seconds: float | None = None
    actions_last_24h: int
