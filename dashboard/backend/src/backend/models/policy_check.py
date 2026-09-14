"""
PolicyCheck — the OPA/Rego verdict on a proposed action (M5/policy module).
Approved decisions move on to human approval; denied ones stop here.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.enums import PolicyVerdict
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class PolicyCheck(Base, TimestampMixin):
    __tablename__ = "policy_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)
    agent_decision_id: Mapped[int] = mapped_column(
        ForeignKey("agent_decisions.id"), nullable=False, index=True
    )

    verdict: Mapped[PolicyVerdict] = mapped_column(Enum(PolicyVerdict, native_enum=False), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=True)  # which Rego rule fired

    incident: Mapped["Incident"] = relationship(back_populates="policy_checks")
