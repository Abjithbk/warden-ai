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
    database_url: str

    # --- Slack ---
    slack_signing_secret: str = ""
    slack_bot_token: str = ""  # xoxb-...  (scope: chat:write)
    slack_channel_id: str = ""  # e.g. C0123ABCDEF (invite the bot to it first)
    slack_api_base_url: str = "https://slack.com/api"
    # Used for the "Open in Warden" link inside Slack messages.
    dashboard_base_url: str = "http://localhost:5173"
    # --- Rate limiting ---
    rate_limit_default: str = "60/minute"

    # --- Dashboard authentication ---
    # Pre-shared key required in the X-API-Key header for dashboard-facing
    # endpoints (e.g. POST /slack/test, POST /slack/notify).
    # Leave empty to disable those endpoints (dependency returns 503).
    dashboard_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    """Cached so we don't re-read env vars on every request."""
    return Settings()
