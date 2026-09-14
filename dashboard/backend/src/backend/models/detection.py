"""
Detection — the raw signal that triggered an incident (e.g. a Prometheus
alert, an OOMKilled event). Produced by the monitoring module (M3);
until then, seeded with realistic fake data.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from backend.models.incident import Incident


class Detection(Base, TimestampMixin):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False, index=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "prometheus", "k8s-events"
    signal: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "OOMKilled", "HighLatency"
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    incident: Mapped["Incident"] = relationship(back_populates="detections")
