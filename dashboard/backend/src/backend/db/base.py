"""
Shared SQLAlchemy declarative base. Every model in models/ inherits from
this Base, and Alembic points at Base.metadata to autogenerate migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
