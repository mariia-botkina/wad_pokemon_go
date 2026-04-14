"""
Router: user-specific endpoints.

Endpoints:
  GET /users/me/collection  – return the authenticated user's caught creatures
                              ordered newest-to-oldest (JWT required)

Future endpoints to add here:
  GET  /users/me            – user profile with stats summary
  PUT  /users/me            – update profile (avatar, display name)
  GET  /users/me/stats      – total catches, unique creatures, etc.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import CaughtCreature, User
from schemas import CollectionResponse, CaughtCreatureResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/collection", response_model=CollectionResponse)
def get_my_collection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated user's personal collection of caught creatures.

    Results are ordered newest-to-oldest (by *caught_at* timestamp) so the most
    recent catch always appears first in the gallery.

    Requires a valid Bearer JWT in the Authorization header.

    Example request:
      GET /users/me/collection
      Authorization: Bearer <token>

    Example response:
      {
        "total": 2,
        "items": [
          {
            "id": 5,
            "caught_at": "2024-01-15T14:32:00Z",
            "creature": {
              "id": 3,
              "name": "Flamara",
              "creature_type": "fire",
              "base_power": 75,
              "description": "A fierce fire creature."
            }
          },
          ...
        ]
      }

    TODO: Add query params for sorting (by name, type, power) once the frontend
          sorting UI is implemented.
    TODO: Add filtering by creature_type once the frontend filter UI is built.
    TODO: Add pagination (skip/limit) for users with large collections.
    TODO: Expose rarity field once creature rarity is added to the Creature model.
    TODO: Add trade_available flag to each item for future creature trading.
    """
    # Query caught creatures for this user, newest first
    caught = (
        db.query(CaughtCreature)
        .filter(CaughtCreature.owner_id == current_user.id)
        .order_by(CaughtCreature.caught_at.desc())
        .all()
    )

    return CollectionResponse(
        total=len(caught),
        items=[CaughtCreatureResponse.model_validate(c) for c in caught],
    )
