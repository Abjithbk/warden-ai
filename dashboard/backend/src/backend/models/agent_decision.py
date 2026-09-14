"""
AgentDecision — output of the AI diagnosis module (M4/Aiswarya's part).
Stores the full step-by-step reasoning trace from LangGraph, not just the
final verdict, so the Incident Detail page can show *why* the agent decided
what it decided.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.enums import ActionType
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class AgentDecision(Base, TimestampMixin):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)

    # Full step-by-step reasoning trace, e.g.
    # [{"step": "analyze_logs", "output": "..."}, {"step": "propose_fix", "output": "..."}]
    reasoning_trace: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    proposed_action: Mapped[ActionType] = mapped_column(Enum(ActionType, native_enum=False), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. deployment/pod name
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    incident: Mapped["Incident"] = relationship(back_populates="agent_decisions")
