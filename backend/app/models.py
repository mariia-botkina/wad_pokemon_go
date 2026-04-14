"""
models.py - SQLAlchemy ORM models for the Pokémon Go-like web app.

Defines database table structures using SQLAlchemy declarative models.

TODO: Add relationships to Creature and Collection models once those are scaffolded.
TODO: Add soft-delete support (deleted_at field) if needed.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String

from .database import Base


class UserRole(str, enum.Enum):
    """
    Enum for user roles in the application.

    - user: Standard player account.
    - admin: Administrator with extra controls and debug access.
    """
    user = "user"
    admin = "admin"


class User(Base):
    """
    SQLAlchemy ORM model for the 'users' table.

    Attributes:
        id (int): Primary key, auto-incremented.
        email (str): Unique email address for the user.
        hashed_password (str): Bcrypt-hashed password string.
        role (UserRole): Role of the user ('user' or 'admin'). Defaults to 'user'.
        created_at (datetime): Timestamp of account creation (UTC).

    TODO: Add email_verified (bool) field and verification flow.
    TODO: Add profile fields (username, avatar_url) for player identity.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        Enum(UserRole, name="userrole"),
        default=UserRole.user,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
