"""
Database engine + session handling.

We use plain (sync) SQLAlchemy sessions here — simpler to reason about than
async sessions, and plenty fast for this project's scale.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings

settings = get_settings()

# PostgreSQL production-grade connection engine with pool pre-ping
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session, always closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
