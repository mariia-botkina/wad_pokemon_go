"""
Pydantic schemas (request/response models) for the API.

Keeping schemas separate from ORM models lets us control exactly what data
enters and leaves the API without accidentally exposing internal fields.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    """Payload required to create a new user account."""
    username: str
    email: str  # Plain str; swap for EmailStr once email-validator is installed
    password: str


class UserLoginRequest(BaseModel):
    """Credentials for obtaining a JWT access token."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT access token returned after successful login/registration."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public-facing user profile (no password hash exposed)."""
    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}


# ── Creatures ─────────────────────────────────────────────────────────────────

class CreatureResponse(BaseModel):
    """Creature template as returned by the API."""
    id: int
    name: str
    creature_type: str
    base_power: int
    description: str

    model_config = {"from_attributes": True}


class SpawnedCreatureResponse(BaseModel):
    """A live creature instance on the map."""
    id: int
    creature_id: int
    latitude: float
    longitude: float
    spawned_at: datetime
    expires_at: datetime
    creature: CreatureResponse

    model_config = {"from_attributes": True}


class CatchRequest(BaseModel):
    """
    Client sends the ID of the spawned creature and its current GPS position
    so the server can validate proximity before confirming the catch.
    """
    spawned_creature_id: int
    user_latitude: float
    user_longitude: float


class CatchResponse(BaseModel):
    """Result returned after a catch attempt."""
    success: bool
    message: str
    caught_creature_id: int | None = None


# ── Collection ────────────────────────────────────────────────────────────────

class CaughtCreatureResponse(BaseModel):
    """
    A single entry in the user's collection.

    Includes all details the frontend needs to render the gallery card:
      - creature name and type
      - base power stat
      - description
      - timestamp of when it was caught (ISO 8601)

    TODO: Add rarity field once creature rarity is implemented.
    TODO: Add catch_latitude/catch_longitude for a map-based history view.
    TODO: Add trade_available flag once creature trading is implemented.
    """
    id: int                   # collection entry ID (unique per catch event)
    caught_at: datetime       # ISO 8601 timestamp – ordered newest-to-oldest
    creature: CreatureResponse  # full creature details nested inline

    model_config = {"from_attributes": True}


class CollectionResponse(BaseModel):
    """
    The full collection returned by GET /users/me/collection.

    Items are ordered newest-to-oldest by caught_at.
    """
    total: int                          # total number of caught creatures
    items: list[CaughtCreatureResponse]  # the collection entries
