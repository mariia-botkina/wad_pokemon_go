"""
Pydantic schemas for the Creature resource.

CreatureBase   - shared fields used by all creature schemas.
CreatureCreate - payload accepted when creating / spawning a creature.
CreatureOut    - response schema returned to API callers.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreatureBase(BaseModel):
    name: str = Field(..., description="Display name of the creature")
    type: str = Field(..., description="Elemental type (e.g. 'fire', 'water', 'grass')")
    latitude: float = Field(..., ge=-90, le=90, description="WGS-84 latitude")
    longitude: float = Field(..., ge=-180, le=180, description="WGS-84 longitude")


class CreatureCreate(CreatureBase):
    """Internal schema used when the spawn utility creates a new creature."""

    expires_at: Optional[datetime] = None


class CreatureOut(CreatureBase):
    """Public schema returned from the API."""

    id: str
    spawned_at: datetime
    expires_at: Optional[datetime] = None
    is_caught: bool

    model_config = {"from_attributes": True}
=======
schemas.py – Pydantic request/response schemas.

TODO: Define UserCreate, UserRead, and UserLogin schemas.
TODO: Define CreatureRead schema (name, type, stats, sprite URL).
TODO: Define SpawnRead schema (creature, latitude, longitude, expires_at).
TODO: Define CatchRequest schema (spawn_id, user latitude/longitude).
"""

# Placeholder – add Pydantic models (schemas) here as the project evolves.
>>>>>>> main
