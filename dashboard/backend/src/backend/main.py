"""
FastAPI Application factory, lifecycle hooks, and router mounting.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.router import api_router
from backend.config import get_settings
from backend.core.middleware import register_middleware
from backend.logging import configure_logging, logger

settings = get_settings()
configure_logging(settings.environment)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("app_startup", environment=settings.environment)
    yield
    logger.info("app_shutdown")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Register rate limiter and CORS
register_middleware(app)

# Mount all endpoints
app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "Warden backend is running"}
