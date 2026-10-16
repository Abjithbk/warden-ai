"""
Dashboard API-key authentication dependency.

Protected endpoints require the caller to present the pre-shared key in the
``X-API-Key`` header.  When ``dashboard_api_key`` is empty in settings the
dependency raises a 503 (misconfigured) rather than silently allowing all
traffic through — fail-closed is the safe default.

Usage::

    from backend.security.dashboard import require_dashboard_auth

    @router.post("/some-endpoint")
    def my_view(_: None = Depends(require_dashboard_auth)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from backend.core.config import Settings, get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_dashboard_auth(
    api_key: str | None = Depends(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """FastAPI dependency — raises 401/503 on failure, returns None on success."""
    if not settings.dashboard_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard authentication is not configured.",
        )
    if api_key != settings.dashboard_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
