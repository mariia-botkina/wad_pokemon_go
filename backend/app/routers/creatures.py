"""
/creatures router – endpoints for spawning and querying nearby creatures.

Endpoints
---------
GET  /creatures/nearby
    Returns a list of creatures currently active within *radius_km* of the
    supplied (lat, lon) coordinates.  Also registers the caller's location
    so the background auto-spawn task can use it.

    Query parameters:
        lat       (float, required) – caller's latitude
        lon       (float, required) – caller's longitude
        radius_km (float, default 0.5) – search radius in kilometres

POST /creatures/spawn  [debug / admin]
    Immediately spawn a batch of random creatures near the given location.
    Useful during development and for the admin debug panel (Step 7).

TODO: Gate POST /creatures/spawn behind an admin role check.
TODO: Add POST /creatures/{id}/catch endpoint with proximity validation.
TODO: Persist creatures to the database instead of in-memory storage.
"""

from fastapi import APIRouter, Query

from ..schemas import CreatureOut
from ..utils.spawn import spawn_manager

router = APIRouter(prefix="/creatures", tags=["creatures"])


@router.get("/nearby", response_model=list[CreatureOut], summary="Get nearby creatures")
def get_nearby_creatures(
    lat: float = Query(..., ge=-90, le=90, description="Caller's latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Caller's longitude"),
    radius_km: float = Query(0.5, gt=0, le=50, description="Search radius in kilometres"),
):
    """Return a list of active, un-caught creatures within *radius_km* of the caller.

    The caller's location is also registered so the background spawn task can
    continue to generate creatures in the same area.

    Example request::

        GET /creatures/nearby?lat=48.8566&lon=2.3522&radius_km=0.5

    Example response::

        [
          {
            "id": "3fa85f64-...",
            "name": "Pikachu",
            "type": "electric",
            "latitude": 48.8571,
            "longitude": 2.3530,
            "spawned_at": "2024-01-01T12:00:00",
            "expires_at": "2024-01-01T12:15:00",
            "is_caught": false
          }
        ]
    """
    # Register location so the background auto-spawn task uses this area.
    spawn_manager.register_location(lat, lon)

    # Seed initial creatures if the pool is completely empty.
    if spawn_manager.is_empty():
        spawn_manager.spawn_batch(lat, lon, count=5, radius_km=radius_km)

    return spawn_manager.get_active(lat, lon, radius_km)


@router.post(
    "/spawn",
    response_model=list[CreatureOut],
    summary="Spawn creatures near a location (debug/admin)",
)
def spawn_creatures(
    lat: float = Query(..., ge=-90, le=90, description="Centre latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Centre longitude"),
    count: int = Query(5, ge=1, le=50, description="Number of creatures to spawn"),
    radius_km: float = Query(0.5, gt=0, le=50, description="Spawn radius in kilometres"),
):
    """Manually trigger a creature spawn batch (intended for admin/debug use).

    TODO: Restrict this endpoint to users with the 'admin' role once
          authentication middleware is wired up.
    """
    return spawn_manager.spawn_batch(lat, lon, count, radius_km)
