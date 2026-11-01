"""
Main router aggregating all versioned and system endpoints.
"""

from fastapi import APIRouter

from backend.api.v1.audit import router as audit_router
from backend.api.v1.health import router as health_router
from backend.api.v1.incidents import router as incidents_router
from backend.api.v1.overview import router as overview_router
from backend.api.v1.slack import router as slack_router
from backend.config import get_settings

settings = get_settings()

api_router = APIRouter()

# Root health check
api_router.include_router(health_router)

# v1 routes mounted together under /api/v1
v1_router = APIRouter(prefix=settings.api_v1_prefix)
v1_router.include_router(overview_router)
v1_router.include_router(incidents_router)
v1_router.include_router(slack_router)
v1_router.include_router(audit_router)

api_router.include_router(v1_router)
