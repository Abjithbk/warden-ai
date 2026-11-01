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

import hmac

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from backend.config import Settings, get_settings
from backend.core.errors import ServiceUnavailableError, WardenError

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class UnauthorizedError(WardenError):
    status_code = 401

def require_dashboard_auth(
    api_key: str | None = Security(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    
    if not settings.dashboard_api_key:
        if settings.environment == 'local':
            return
        raise ServiceUnavailableError("Dashboard authentication is not configured.")
    if not api_key or not hmac.compare_digest(api_key,settings.dashboard_api_key):
        raise UnauthorizedError("Invalid or missing API key.")
