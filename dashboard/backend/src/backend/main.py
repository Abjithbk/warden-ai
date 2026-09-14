from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.healthz import router as healthz_router
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

app.include_router(healthz_router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("app_startup", environment=settings.environment)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "Warden backend is running"}
