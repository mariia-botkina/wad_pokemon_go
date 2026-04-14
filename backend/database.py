"""
Database configuration and session management.

Uses SQLite for local development (no PostgreSQL required to run locally).
Replace DATABASE_URL with a PostgreSQL URL for production, e.g.:
  postgresql://user:password@localhost:5432/pokemon_go_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite for local dev; swap for PostgreSQL in production
DATABASE_URL = "sqlite:///./pokemon_go.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_db():
    """FastAPI dependency: yields a DB session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
