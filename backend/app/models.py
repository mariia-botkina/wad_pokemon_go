"""
SQLAlchemy ORM models.

Creature – represents a single spawned creature on the map.
  Fields:
    id          – primary key (UUID string)
    name        – display name of the creature (e.g. "Bulbasaur")
    type        – creature type (e.g. "grass", "fire", "water")
    latitude    – WGS-84 latitude of the spawn point
    longitude   – WGS-84 longitude of the spawn point
    spawned_at  – UTC timestamp when the creature appeared
    expires_at  – UTC timestamp when the creature despawns (NULL = never)
    is_caught   – whether the creature has already been caught by a user

TODO: Add a ForeignKey to a CreatureLibrary table for full creature metadata.
TODO: Add a ForeignKey to User once catching is implemented.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, String

from .database import Base


class Creature(Base):
    __tablename__ = "creatures"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    spawned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_caught = Column(Boolean, default=False, nullable=False)
