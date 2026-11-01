from fastapi import APIRouter

from backend.api.v1 import audit, health, incidents, overview, slack
from backend.config import get_settings

api_router = APIRouter()

# Root health check
api_router.include_router(health.router)

# v1 routes — auth will be added here when JWT is implemented
v1 = APIRouter(prefix=get_settings().api_v1_prefix)
v1.include_router(overview.router)
v1.include_router(incidents.router)
v1.include_router(slack.router)
v1.include_router(audit.router)
v1.include_router(slack.webhook_router)

api_router.include_router(v1)
