"""
Pydantic schemas for the Incident API responses. Kept separate from the
SQLAlchemy models — models describe storage, schemas describe the API
contract the frontend depends on.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.models.enums import IncidentSeverity, IncidentStatus


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
