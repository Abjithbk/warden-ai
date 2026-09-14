"""
Importing every model here ensures they're all registered on Base.metadata
before Alembic (or anything else) inspects it. Without this, Alembic's
autogenerate would silently miss tables.
"""

from backend.models.agent_decision import AgentDecision
from backend.models.approval_request import ApprovalRequest
from backend.models.audit_log_entry import AuditLogEntry
from backend.models.detection import Detection
from backend.models.incident import Incident
from backend.models.policy_check import PolicyCheck
from backend.models.remediation_action import RemediationAction

__all__ = [
    "AgentDecision",
    "ApprovalRequest",
    "AuditLogEntry",
    "Detection",
    "Incident",
    "PolicyCheck",
    "RemediationAction",
]
