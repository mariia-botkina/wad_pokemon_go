"""
Database connection and session management.

Uses SQLAlchemy with a PostgreSQL backend (configured via DATABASE_URL env var).
Falls back to SQLite for local/test development when DATABASE_URL is not set.

TODO: Add Alembic migrations once the schema stabilises.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pokemon_go.db")

# For SQLite (used in tests / local dev without Postgres), allow multi-thread access.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
