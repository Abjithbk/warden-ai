from fastapi import APIRouter, Depends

from backend.api.v1 import audit, health, incidents, overview, slack
from backend.config import get_settings
from backend.security.dashboard import require_dashboard_auth

api_router = APIRouter()

# Root health check
api_router.include_router(health.router)

auth = [Depends(require_dashboard_auth)]
v1 = APIRouter(prefix=get_settings().api_v1_prefix)
v1.include_router(overview.router,dependencies=auth)
v1.include_router(incidents.router,dependencies=auth)
v1.include_router(slack.router,dependencies=auth)
v1.include_router(audit.router,dependencies=auth)
v1.include_router(slack.webhook_router)

api_router.include_router(v1)
