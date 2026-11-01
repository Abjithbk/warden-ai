"""
Incident domain models.
Centralizes Incident and all related child records that compose the remediation trace:
Detection, AgentDecision, PolicyCheck, ApprovalRequest, and RemediationAction.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.enums import (
    ActionStatus,
    ActionType,
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    PolicyVerdict,
)

if TYPE_CHECKING:
    from backend.models.audit import AuditLogEntry


class TimestampMixin:
    """Reusable mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    service: Mapped[str] = mapped_column(String(255), nullable=False)
    namespace: Mapped[str] = mapped_column(String(255), nullable=False)

    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, native_enum=False), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, native_enum=False),
        nullable=False,
        default=IncidentStatus.active,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    detections: Mapped[list["Detection"]] = relationship(
        back_populates="incident",
        order_by="Detection.created_at",
        cascade="all, delete-orphan",
    )
    agent_decisions: Mapped[list["AgentDecision"]] = relationship(
        back_populates="incident",
        order_by="AgentDecision.created_at",
        cascade="all, delete-orphan",
    )
    policy_checks: Mapped[list["PolicyCheck"]] = relationship(
        back_populates="incident",
        order_by="PolicyCheck.created_at",
        cascade="all, delete-orphan",
    )
    approval_requests: Mapped[list["ApprovalRequest"]] = relationship(
        back_populates="incident",
        order_by="ApprovalRequest.created_at",
        cascade="all, delete-orphan",
    )
    remediation_actions: Mapped[list["RemediationAction"]] = relationship(
        back_populates="incident",
        order_by="RemediationAction.created_at",
        cascade="all, delete-orphan",
    )
    audit_log_entries: Mapped[list["AuditLogEntry"]] = relationship(
        back_populates="incident",
        order_by="AuditLogEntry.created_at",
        cascade="all, delete-orphan",
    )


class Detection(Base, TimestampMixin):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    signal: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    incident: Mapped["Incident"] = relationship(back_populates="detections")


class AgentDecision(Base, TimestampMixin):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    reasoning_trace: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    proposed_action: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False), nullable=False
    )
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    incident: Mapped["Incident"] = relationship(back_populates="agent_decisions")


class PolicyCheck(Base, TimestampMixin):
    __tablename__ = "policy_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    agent_decision_id: Mapped[int] = mapped_column(
        ForeignKey("agent_decisions.id"), nullable=False, index=True
    )
    verdict: Mapped[PolicyVerdict] = mapped_column(
        Enum(PolicyVerdict, native_enum=False), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=True)

    incident: Mapped["Incident"] = relationship(back_populates="policy_checks")


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
    actioned_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    actioned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    slack_channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    slack_message_ts: Mapped[str | None] = mapped_column(String(64), nullable=True)

    incident: Mapped["Incident"] = relationship(back_populates="approval_requests")


class RemediationAction(Base, TimestampMixin):
    __tablename__ = "remediation_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"), nullable=False, index=True
    )
    approval_request_id: Mapped[int] = mapped_column(
        ForeignKey("approval_requests.id"), nullable=False, index=True
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False), nullable=False
    )
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, native_enum=False),
        nullable=False,
        default=ActionStatus.pending,
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    incident: Mapped["Incident"] = relationship(back_populates="remediation_actions")
