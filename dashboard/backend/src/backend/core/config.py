"""
Application settings, loaded from environment variables (or a local .env file).

Never hardcode config values in code — add them here, with a sensible default
only for genuinely non-secret local-dev values.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Warden Dashboard API"
    environment: str = "local"  # local | staging | production
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Database ---
    # SQLite for local dev by default. Swap to Postgres later by changing
    # this one value, e.g. postgresql+psycopg://user:pass@host:5432/warden
    database_url: str = "sqlite:///./warden.db"

    # --- Slack ---
    slack_signing_secret: str = ""

    # --- Rate limiting ---
    rate_limit_default: str = "60/minute"


@lru_cache
def get_settings() -> Settings:
    """Cached so we don't re-read env vars on every request."""
    return Settings()
