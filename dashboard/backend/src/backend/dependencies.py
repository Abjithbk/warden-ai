"""
Common FastAPI dependency providers (DB session, auth checks).
"""

from collections.abc import Generator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session per request, ensuring cleanup on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_dashboard_auth(authorization: str | None = Header(default=None)) -> None:
    """Verifies the bearer token against DASHBOARD_API_KEY when configured."""
    settings = get_settings()
    if not settings.dashboard_api_key:
        return

    expected = f"Bearer {settings.dashboard_api_key}"
    if not authorization or authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
