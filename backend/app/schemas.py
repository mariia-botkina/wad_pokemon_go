"""
schemas.py - Pydantic schemas for request/response validation and serialization.

Schemas are used for data validation in API endpoints and for shaping responses
sent back to clients. They are separate from SQLAlchemy models to keep
concerns cleanly separated.

TODO: Add schemas for Creature, Collection, and other game entities.
TODO: Add pagination schemas (PagedResponse) when list endpoints are added.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from .models import UserRole


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """
    Schema for user registration request body.

    Fields:
        email (EmailStr): Valid email address for the new account.
        password (str): Plain-text password (will be hashed server-side).
    """
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        """Ensure the password meets a minimum length requirement."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value


class LoginRequest(BaseModel):
    """
    Schema for user login request body.

    Fields:
        email (EmailStr): Registered email address.
        password (str): Plain-text password to verify.
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Schema for JWT token response returned after successful authentication.

    Fields:
        access_token (str): Signed JWT access token.
        token_type (str): Token scheme, always 'bearer'.
    """
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    """
    Shared base schema for user data.

    Fields:
        email (EmailStr): User's email address.
        role (UserRole): User role ('user' or 'admin').
    """
    email: EmailStr
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    """
    Schema for creating a new user (includes plain-text password).

    Fields:
        password (str): Plain-text password to be hashed before storage.
    """
    password: str


class UserRead(UserBase):
    """
    Schema for reading user data returned to API clients.

    Excludes sensitive fields like hashed_password.

    Fields:
        id (int): Unique user identifier.
        created_at (datetime): Account creation timestamp.
    """
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """
    Schema for partial user update requests.

    All fields are optional so clients can send only what they want to change.

    TODO: Add more fields (username, avatar_url) as they are added to the model.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
