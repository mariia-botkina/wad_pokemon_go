"""
routes.py - API route definitions for authentication and user management.

Provides the following endpoints:
- POST /register  - Create a new user account.
- POST /login     - Authenticate a user and return a JWT token.
- GET  /users/me  - Get the currently authenticated user's profile.
- GET  /users     - List all users (admin only).
- DELETE /users/{user_id} - Delete a user by ID (admin only).

TODO: Add PUT /users/me for profile update.
TODO: Add admin-only user role management endpoint.
TODO: Add rate limiting on /register and /login to prevent abuse.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .auth import create_access_token, decode_access_token, hash_password, verify_password
from .database import get_db
from .models import User, UserRole
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead

router = APIRouter()

# OAuth2 scheme: clients send the token as a Bearer token in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ---------------------------------------------------------------------------
# Dependency: get the current authenticated user from the JWT token
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that resolves the current user from the provided JWT token.

    Raises:
        HTTPException 401: If the token is invalid, expired, or the user is not found.

    Returns:
        User: The authenticated user ORM object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user has the 'admin' role.

    Raises:
        HTTPException 403: If the user is not an admin.

    Returns:
        User: The authenticated admin user ORM object.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by email address.

    Args:
        db (Session): Active database session.
        email (str): Email address to search for.

    Returns:
        User | None: The matching User object, or None if not found.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Retrieve a user from the database by primary key.

    Args:
        db (Session): Active database session.
        user_id (int): The user's primary key ID.

    Returns:
        User | None: The matching User object, or None if not found.
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, plain_password: str, role: UserRole = UserRole.user) -> User:
    """
    Create and persist a new user record in the database.

    Args:
        db (Session): Active database session.
        email (str): Email address for the new account.
        plain_password (str): Plain-text password (will be hashed).
        role (UserRole): Role to assign to the new user. Defaults to 'user'.

    Returns:
        User: The newly created and committed User ORM object.
    """
    hashed = hash_password(plain_password)
    new_user = User(email=email, hashed_password=hashed, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.

    - Validates email uniqueness.
    - Hashes the password before storage.
    - Returns the created user (without sensitive fields).

    Raises:
        HTTPException 400: If the email is already registered.
    """
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    user = create_user(db, email=payload.email, plain_password=payload.password)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user with email and password.

    - Verifies the user exists and the password matches.
    - Returns a signed JWT access token on success.

    Raises:
        HTTPException 401: If credentials are invalid.
    """
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# User endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/users/me",
    response_model=UserRead,
    summary="Get the currently authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.

    Requires a valid Bearer token in the Authorization header.
    """
    return current_user


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="List all users (admin only)",
)
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """
    Return a list of all registered users.

    Requires admin role. Intended for admin/debug panels.

    TODO: Add pagination (skip/limit query parameters).
    """
    return db.query(User).all()


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user by ID (admin only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """
    Delete a user account by their numeric ID.

    Requires admin role.

    Raises:
        HTTPException 404: If no user with the given ID exists.

    TODO: Consider soft-delete instead of hard-delete for audit trail.
    """
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )
    db.delete(user)
    db.commit()
