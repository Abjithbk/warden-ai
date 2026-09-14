"""
RemediationAction — the actual action taken once approved (executor
module). Limited to the four whitelisted ActionType values — never
arbitrary code execution.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.enums import ActionStatus, ActionType
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class RemediationAction(Base, TimestampMixin):
    __tablename__ = "remediation_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)
    approval_request_id: Mapped[int] = mapped_column(
        ForeignKey("approval_requests.id"), nullable=False, index=True
    )

    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType, native_enum=False), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, native_enum=False), nullable=False, default=ActionStatus.pending
    )

    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    incident: Mapped["Incident"] = relationship(back_populates="remediation_actions")
