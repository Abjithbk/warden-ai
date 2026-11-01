"""
Application settings, loaded from environment variables (or a local .env file).

Never hardcode config values in code — add them here, with a sensible default
only for genuinely non-secret local-dev values.
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Warden Dashboard API"
    environment: Literal['local','staging','production'] = 'local'
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

   
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
    @field_validator("cors_origins",mode="before")
    @classmethod

    def _split_origins(cls,v):
        if isinstance(v,str):
            v= v.strip()
            if v.startswith("["):
                import json

                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

@lru_cache
def get_settings() -> Settings:
    """Cached so we don't re-read env vars on every request."""
    return Settings()
