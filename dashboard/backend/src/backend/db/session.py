"""
Database engine + session handling.

We use plain (sync) SQLAlchemy sessions here — simpler to reason about than
async sessions, and plenty fast for this project's scale.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import get_settings

settings = get_settings()

# check_same_thread=False is only needed for SQLite (FastAPI may use the
# connection from a different thread than it was created in). It's ignored
# by other database drivers.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session, always closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
