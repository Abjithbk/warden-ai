from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.healthz import router as healthz_router
from backend.api.v1.incidents import router as incidents_router
from backend.api.v1.overview import router as overview_router
from backend.core.config import get_settings
from backend.core.logging import configure_logging, logger

settings = get_settings()
configure_logging(settings.environment)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers that don't carry the /api/v1 prefix (e.g. health checks)
app.include_router(healthz_router)

# Versioned API routers
app.include_router(overview_router, prefix=settings.api_v1_prefix)
app.include_router(incidents_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("app_startup", environment=settings.environment)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "Warden backend is running"}
