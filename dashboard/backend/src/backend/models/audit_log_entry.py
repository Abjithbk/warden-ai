"""
AuditLogEntry — the append-only audit trail. Every meaningful state change
(approved, rejected, action executed, action failed, etc.) writes one of
these. This is what GET /api/v1/audit and its CSV export read from.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class AuditLogEntry(Base, TimestampMixin):
    __tablename__ = "audit_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)

    # e.g. "slack:U0123ABC", "dashboard:amaya", "system"
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    # e.g. "incident_created", "approval_approved", "action_succeeded"
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    incident: Mapped["Incident"] = relationship(back_populates="audit_log_entries")
