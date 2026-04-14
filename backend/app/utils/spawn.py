"""
In-memory creature spawn manager.

Handles periodic spawning of creatures within a geofence around a user's last
known location.  The active creature pool is held in memory for simplicity;
a production implementation should persist creatures in the database so they
survive restarts and are shared across server instances.

Public API
----------
SpawnManager.spawn_batch(lat, lon, count, radius_km)
    Immediately generate *count* creatures near (lat, lon) and store them.

SpawnManager.get_active(lat, lon, radius_km)
    Return all non-expired creatures within *radius_km* of (lat, lon).

SpawnManager.tick()
    Remove expired creatures.  Called by the background task.

Background task
---------------
The module also exposes ``start_spawn_task`` which, when passed to FastAPI's
``lifespan`` context, starts a periodic background coroutine that:
  1. Calls ``tick()`` to remove expired creatures.
  2. Periodically emits a small batch of new creatures near the most-recently
     registered user location.

TODO: Replace in-memory storage with a database-backed approach so creatures
      persist across restarts and are visible to all connected users.
TODO: Track each user's location separately for multi-user support.
TODO: Implement WebSocket push so clients receive live spawn events.
"""

import asyncio
import math
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from ..schemas import CreatureCreate, CreatureOut
from .creature_generator import generate_creature

# ---------------------------------------------------------------------------
# Haversine distance helper
# ---------------------------------------------------------------------------


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in kilometres between two WGS-84 points.

    Uses the Haversine formula, which is accurate for all distances on Earth.

    Parameters
    ----------
    lat1, lon1: first point in decimal degrees
    lat2, lon2: second point in decimal degrees

    Returns
    -------
    Distance in kilometres as a float.

    Examples
    --------
    >>> round(haversine_km(48.8566, 2.3522, 51.5074, -0.1278), 0)
    341.0
    """
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# In-memory spawn manager
# ---------------------------------------------------------------------------


class SpawnManager:
    """Manages the lifecycle of spawned creatures in memory.

    Attributes
    ----------
    _creatures: dict[str, CreatureOut]  Active creature pool keyed by id.
    """

    def __init__(self) -> None:
        self._creatures: dict[str, CreatureOut] = {}
        # Last known user location – used by the background auto-spawn task.
        self._last_lat: float = 0.0
        self._last_lon: float = 0.0

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def register_location(self, lat: float, lon: float) -> None:
        """Update the most-recently seen user location for background spawns."""
        self._last_lat = lat
        self._last_lon = lon

    def spawn_batch(
        self,
        lat: float,
        lon: float,
        count: int = 5,
        radius_km: float = 0.5,
    ) -> list[CreatureOut]:
        """Generate *count* creatures near (lat, lon) and add them to the pool.

        Parameters
        ----------
        lat, lon:   centre of the spawn area
        count:      number of creatures to spawn
        radius_km:  radius of the spawn circle

        Returns
        -------
        List of newly spawned :class:`~app.schemas.CreatureOut` objects.
        """
        spawned: list[CreatureOut] = []
        for _ in range(count):
            schema: CreatureCreate = generate_creature(lat, lon, radius_km)
            creature = CreatureOut(
                id=str(uuid.uuid4()),
                name=schema.name,
                type=schema.type,
                latitude=schema.latitude,
                longitude=schema.longitude,
                spawned_at=datetime.now(timezone.utc),
                expires_at=schema.expires_at,
                is_caught=False,
            )
            self._creatures[creature.id] = creature
            spawned.append(creature)
        return spawned

    def get_active(
        self,
        lat: float,
        lon: float,
        radius_km: float = 0.5,
    ) -> list[CreatureOut]:
        """Return all non-expired, un-caught creatures within *radius_km*.

        The method also prunes expired entries as a side-effect.

        Parameters
        ----------
        lat, lon:   user's current position
        radius_km:  search radius in kilometres

        Returns
        -------
        List of :class:`~app.schemas.CreatureOut` objects within range.
        """
        self.tick()
        now = datetime.now(timezone.utc)
        result: list[CreatureOut] = []
        for creature in self._creatures.values():
            if creature.is_caught:
                continue
            if creature.expires_at and creature.expires_at < now:
                continue
            dist = haversine_km(lat, lon, creature.latitude, creature.longitude)
            if dist <= radius_km:
                result.append(creature)
        return result

    def tick(self) -> int:
        """Remove all expired creatures from the pool.

        Returns
        -------
        Number of creatures removed.
        """
        now = datetime.now(timezone.utc)
        expired = [
            cid
            for cid, c in self._creatures.items()
            if c.expires_at and c.expires_at < now
        ]
        for cid in expired:
            del self._creatures[cid]
        return len(expired)

    def is_empty(self) -> bool:
        """Return True if there are no creatures in the pool."""
        return len(self._creatures) == 0

    # ------------------------------------------------------------------
    # Background auto-spawn task
    # ------------------------------------------------------------------

    async def auto_spawn_loop(
        self,
        interval_seconds: int = 30,
        batch_size: int = 3,
        radius_km: float = 0.5,
    ) -> None:
        """Coroutine that spawns new creatures near the last known location.

        Runs indefinitely; cancel via the task returned by asyncio.create_task.

        Parameters
        ----------
        interval_seconds: seconds between each spawn cycle
        batch_size:       creatures to spawn per cycle
        radius_km:        spawn radius around the last known user location
        """
        while True:
            await asyncio.sleep(interval_seconds)
            self.tick()
            if self._last_lat != 0.0 or self._last_lon != 0.0:
                self.spawn_batch(self._last_lat, self._last_lon, batch_size, radius_km)


# Module-level singleton shared across the application.
spawn_manager = SpawnManager()


@asynccontextmanager
async def spawn_lifespan(app):  # noqa: ARG001
    """FastAPI lifespan context: starts the background spawn task on startup.

    Renamed from ``lifespan`` to avoid shadowing FastAPI's own ``lifespan``
    parameter name and to make the purpose explicit.

    Usage::

        app = FastAPI(lifespan=spawn_lifespan)
    """
    task = asyncio.create_task(spawn_manager.auto_spawn_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
