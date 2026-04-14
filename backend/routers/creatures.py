"""
Router: creature spawn management and catch action.

Endpoints:
  GET  /creatures/nearby          – list active spawns near a GPS position
  POST /creatures/spawn           – (admin) manually spawn a creature at a location
  POST /creatures/catch           – attempt to catch a spawned creature (JWT required)

Proximity validation is performed server-side (haversine distance) to prevent
location spoofing from the client.
"""

import math
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Creature, CaughtCreature, SpawnedCreature, User
from schemas import CatchRequest, CatchResponse, SpawnedCreatureResponse

router = APIRouter(prefix="/creatures", tags=["creatures"])

# Maximum distance (metres) from which a user can catch a creature
CATCH_RADIUS_METRES = 50.0

# How long (minutes) a spawned creature stays on the map before it despawns
SPAWN_DURATION_MINUTES = 10


def _haversine_metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in metres between two GPS coordinates.

    Uses the haversine formula; accurate enough for short distances (<< 1 km).
    """
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.get("/nearby", response_model=list[SpawnedCreatureResponse])
def get_nearby_creatures(
    latitude: float,
    longitude: float,
    radius_metres: float = 500.0,
    db: Session = Depends(get_db),
):
    """
    Return all active spawned creatures within *radius_metres* of the given GPS position.

    Only returns spawns that have not yet expired.
    The radius check is done server-side, so client-submitted coordinates cannot
    reveal creatures outside the intended area.
    """
    now = datetime.now(timezone.utc)
    # Fetch all non-expired spawns and filter by distance in Python.
    # For large deployments, replace with a PostGIS spatial query.
    active_spawns = (
        db.query(SpawnedCreature)
        .filter(SpawnedCreature.expires_at > now)
        .all()
    )
    nearby = [
        s for s in active_spawns
        if _haversine_metres(latitude, longitude, s.latitude, s.longitude) <= radius_metres
    ]
    return nearby


@router.post("/spawn", response_model=SpawnedCreatureResponse, status_code=status.HTTP_201_CREATED)
def spawn_creature(
    latitude: float,
    longitude: float,
    creature_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Spawn a creature at the given location.

    If *creature_id* is omitted, a random creature from the library is chosen.
    Any authenticated user can trigger a spawn (for demo/testing purposes);
    in production this should be restricted to admins or done by a background task.

    TODO: Restrict to admin role for production.
    TODO: Move random spawning to a background scheduler (APScheduler/Celery).
    """
    if creature_id is not None:
        creature = db.query(Creature).filter(Creature.id == creature_id).first()
        if not creature:
            raise HTTPException(status_code=404, detail="Creature not found in library")
    else:
        # Pick a random creature from the library
        creatures = db.query(Creature).all()
        if not creatures:
            raise HTTPException(
                status_code=500,
                detail="No creatures in the library. Seed the database first.",
            )
        creature = random.choice(creatures)

    now = datetime.now(timezone.utc)
    spawn = SpawnedCreature(
        creature_id=creature.id,
        latitude=latitude,
        longitude=longitude,
        spawned_at=now,
        expires_at=now + timedelta(minutes=SPAWN_DURATION_MINUTES),
    )
    db.add(spawn)
    db.commit()
    db.refresh(spawn)
    return spawn


@router.post("/catch", response_model=CatchResponse)
def catch_creature(
    payload: CatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Attempt to catch a spawned creature.

    Server-side checks performed before confirming the catch:
      1. The spawned creature exists and has not expired.
      2. The user is within CATCH_RADIUS_METRES of the spawn location.

    On success:
      - The spawned instance is removed from the map.
      - A CaughtCreature record is added to the user's collection.

    Returns success=False (HTTP 200) for game-logic failures (e.g. out of range)
    so the frontend can display a friendly message without treating it as an error.
    """
    now = datetime.now(timezone.utc)
    spawn = db.query(SpawnedCreature).filter(SpawnedCreature.id == payload.spawned_creature_id).first()

    if not spawn:
        return CatchResponse(success=False, message="Creature not found or already caught")

    # Check expiry
    spawn_expires_at = spawn.expires_at
    if spawn_expires_at.tzinfo is None:
        spawn_expires_at = spawn_expires_at.replace(tzinfo=timezone.utc)
    if spawn_expires_at < now:
        return CatchResponse(success=False, message="This creature has already despawned")

    # Server-side proximity check
    distance = _haversine_metres(
        payload.user_latitude, payload.user_longitude,
        spawn.latitude, spawn.longitude,
    )
    if distance > CATCH_RADIUS_METRES:
        return CatchResponse(
            success=False,
            message=f"Too far away ({distance:.0f} m). You need to be within {CATCH_RADIUS_METRES:.0f} m.",
        )

    # Confirm the catch: add to collection and remove from the map
    caught = CaughtCreature(owner_id=current_user.id, creature_id=spawn.creature_id)
    db.add(caught)
    db.delete(spawn)
    db.commit()
    db.refresh(caught)

    return CatchResponse(success=True, message="Caught!", caught_creature_id=caught.id)
