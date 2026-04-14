"""
auth.py - Authentication utilities: password hashing and JWT token management.

Provides helper functions for:
- Hashing and verifying passwords using bcrypt (via passlib).
- Creating and decoding JWT access tokens (via python-jose).

TODO: Add refresh token support for longer-lived sessions.
TODO: Add token revocation/blacklist when logout is implemented.
TODO: Integrate OAuth (Google, Apple) token verification here.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# Load environment variables from .env file
load_dotenv()

# Secret key used to sign JWT tokens.
# MUST be a long random string in production. Set via environment variable.
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-secret-key")

# JWT signing algorithm
ALGORITHM: str = "HS256"

# Access token lifetime in minutes (default: 60 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Passlib CryptContext configured for bcrypt password hashing.
# deprecated="auto" ensures old hashes are upgraded automatically.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password (str): The user's plain-text password.

    Returns:
        str: The bcrypt-hashed password string suitable for database storage.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password (str): The password provided by the user at login.
        hashed_password (str): The stored bcrypt hash from the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data (dict): Payload data to encode in the token (e.g., {"sub": user_email}).
        expires_delta (timedelta, optional): Custom expiration duration.
            Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Args:
        token (str): The JWT token string to decode.

    Returns:
        dict: The decoded token payload if valid.
        None: If the token is invalid or expired.

    TODO: Raise specific HTTPException types for clearer error handling.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
