"""
Audit domain models.
Stores append-only audit trail logs for all remediation and approval events.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.incident import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class AuditLogEntry(Base, TimestampMixin):
    __tablename__ = "audit_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    incident: Mapped["Incident"] = relationship(back_populates="audit_log_entries")
