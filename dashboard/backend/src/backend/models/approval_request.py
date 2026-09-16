
"""
ApprovalRequest — the human approval gate blocking Act/Observe. Can be
actioned from the dashboard or from Slack, so `actioned_at` is what the
approve/reject endpoints check to return 409 if it's already been decided
(prevents Slack + Dashboard racing each other on the same request).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.enums import ApprovalStatus
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class ApprovalRequest(Base, TimestampMixin):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    policy_check_id: Mapped[int] = mapped_column(
        ForeignKey("policy_checks.id"), nullable=False, index=True
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False),
        nullable=False,
        default=ApprovalStatus.pending,
    )

    # Who approved/rejected it, e.g. "dashboard:amaya" or "slack:U0123ABC"
    actioned_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Set the moment approve/reject succeeds. NULL = still pending.
    # The approve/reject endpoints check this first: if it's already set,
    # return 409 instead of double-actioning.
    actioned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="approval_requests"
    )

