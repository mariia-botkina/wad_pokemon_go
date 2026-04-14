"""
Random creature generator utility.

Provides a pool of pre-defined creature templates and a factory function that
produces a fully-populated CreatureCreate instance at a random location near
a given origin point.

Usage
-----
>>> from app.utils.creature_generator import generate_creature
>>> creature = generate_creature(lat=48.8566, lon=2.3522, radius_km=0.5)

TODO: Replace the static CREATURE_TEMPLATES list with a database-backed
      CreatureLibrary table so admins can add/edit creatures without code
      changes (see Step 8 in docs/PLANNING.md).
"""

import math
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..schemas import CreatureCreate

# ---------------------------------------------------------------------------
# Static creature template library
# ---------------------------------------------------------------------------

CREATURE_TEMPLATES = [
    {"name": "Bulbasaur", "type": "grass"},
    {"name": "Charmander", "type": "fire"},
    {"name": "Squirtle", "type": "water"},
    {"name": "Pikachu", "type": "electric"},
    {"name": "Gengar", "type": "ghost"},
    {"name": "Machop", "type": "fighting"},
    {"name": "Geodude", "type": "rock"},
    {"name": "Gastly", "type": "ghost"},
    {"name": "Eevee", "type": "normal"},
    {"name": "Snorlax", "type": "normal"},
    {"name": "Magikarp", "type": "water"},
    {"name": "Jigglypuff", "type": "fairy"},
    {"name": "Meowth", "type": "normal"},
    {"name": "Psyduck", "type": "water"},
    {"name": "Abra", "type": "psychic"},
]

# How long (minutes) a spawned creature remains on the map before despawning.
DEFAULT_LIFESPAN_MINUTES = 15


def _random_offset(lat: float, lon: float, radius_km: float) -> tuple[float, float]:
    """Return a random (lat, lon) within *radius_km* kilometres of the origin.

    Uses a simple equirectangular approximation which is accurate enough for
    small radii (< 10 km).

    Parameters
    ----------
    lat:       origin latitude in decimal degrees
    lon:       origin longitude in decimal degrees
    radius_km: maximum distance from origin in kilometres

    Returns
    -------
    (new_lat, new_lon) as a tuple of floats
    """
    # 1 degree of latitude ≈ 111.32 km
    lat_delta = radius_km / 111.32
    # Longitude degrees shrink with latitude
    lon_delta = radius_km / (111.32 * math.cos(math.radians(lat)))

    new_lat = lat + random.uniform(-lat_delta, lat_delta)
    new_lon = lon + random.uniform(-lon_delta, lon_delta)
    return new_lat, new_lon


def generate_creature(
    lat: float,
    lon: float,
    radius_km: float = 0.5,
    lifespan_minutes: Optional[int] = DEFAULT_LIFESPAN_MINUTES,
) -> CreatureCreate:
    """Generate a single random creature near the given location.

    Parameters
    ----------
    lat:              centre latitude for the spawn area
    lon:              centre longitude for the spawn area
    radius_km:        radius of the spawn circle in kilometres (default 0.5 km)
    lifespan_minutes: minutes until the creature despawns; None means no expiry

    Returns
    -------
    A :class:`~app.schemas.CreatureCreate` instance ready to be persisted.

    Examples
    --------
    >>> c = generate_creature(48.8566, 2.3522, radius_km=0.3)
    >>> assert c.type in [t["type"] for t in CREATURE_TEMPLATES]
    >>> assert -90 <= c.latitude <= 90
    """
    template = random.choice(CREATURE_TEMPLATES)
    spawn_lat, spawn_lon = _random_offset(lat, lon, radius_km)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=lifespan_minutes) if lifespan_minutes else None

    return CreatureCreate(
        name=template["name"],
        type=template["type"],
        latitude=round(spawn_lat, 6),
        longitude=round(spawn_lon, 6),
        expires_at=expires_at,
    )
