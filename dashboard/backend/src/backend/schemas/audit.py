"""
Schemas for the audit log endpoints — GET /audit (paginated JSON) and
GET /audit/export (CSV of the same filtered set).
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogEntryOut(BaseModel):
    id: int
    incident_id: int
    actor: str
    action: str
    detail: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListOut(BaseModel):
    items: list[AuditLogEntryOut]
    total: int
    limit: int
    offset: int