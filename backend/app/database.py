"""
database.py - SQLAlchemy engine and session setup for PostgreSQL.

This module creates the database engine, session factory, and declarative base
used throughout the application for ORM model definitions and database access.

TODO: Add connection pooling configuration for production use.
TODO: Add support for async SQLAlchemy (asyncpg) when scaling requires it.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# DATABASE_URL should be set in the .env file.
# Example: postgresql://user:password@localhost:5432/pokemon_go_db
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pokemon_go_db")

# Create the SQLAlchemy engine.
# pool_pre_ping=True enables connection health checks before use.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is the database session factory.
# autocommit=False and autoflush=False are recommended defaults for FastAPI.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session for each request.

    Yields a SQLAlchemy session and ensures it is closed after the request
    completes, even if an exception occurs.

    Usage in FastAPI route:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
