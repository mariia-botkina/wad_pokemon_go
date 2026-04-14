"""
SQLAlchemy ORM models for the Pokémon Go-like app.

Models:
  - User            : registered player account
  - Creature        : creature template (the "library" of all possible creatures)
  - SpawnedCreature : a creature instance currently active on the map
  - CaughtCreature  : a creature in a user's personal collection (caught event)

Future extensions:
  - Add rarity field to Creature for rarity-based filtering / trading
  - Add evolution_chain_id for creature evolution trees
  - Add trade_history table for creature trading between users
"""

import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    Registered user account.

    Roles: "user" (default) or "admin" (extra controls).
    Password is stored as a bcrypt hash – never plain text.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # "user" | "admin"
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationship to the user's caught creatures (their collection)
    caught_creatures = relationship(
        "CaughtCreature", back_populates="owner", order_by="CaughtCreature.caught_at.desc()"
    )


class Creature(Base):
    """
    Creature template – the authoritative library of all available creatures.

    Each creature has a name, elemental type, and base power stat.
    TODO: Add rarity field (common/uncommon/rare/legendary) for future
          rarity-based filtering and display in the gallery.
    TODO: Add sprite_url field once asset hosting is set up.
    """
    __tablename__ = "creatures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    creature_type = Column(String, nullable=False)  # e.g. "fire", "water", "grass"
    base_power = Column(Integer, default=50, nullable=False)
    description = Column(String, default="", nullable=False)

    # Relationship to all map instances of this creature
    spawned_instances = relationship("SpawnedCreature", back_populates="creature")
    caught_instances = relationship("CaughtCreature", back_populates="creature")


class SpawnedCreature(Base):
    """
    An active creature instance currently visible on the map.

    Created by the spawn logic; removed when caught or when it despawns.
    Latitude/longitude are server-side – client cannot forge a spawn location.
    """
    __tablename__ = "spawned_creatures"

    id = Column(Integer, primary_key=True, index=True)
    creature_id = Column(Integer, ForeignKey("creatures.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    spawned_at = Column(DateTime, default=func.now(), nullable=False)
    # Expiry is set by spawn logic (e.g. 10 minutes after spawn)
    expires_at = Column(DateTime, nullable=False)

    creature = relationship("Creature", back_populates="spawned_instances")


class CaughtCreature(Base):
    """
    A catch event – records that a specific user caught a specific creature.

    This forms the user's personal collection / gallery.
    Each row represents one catch (a user may catch the same creature type
    multiple times, producing multiple rows).

    TODO: Add lat/lon of catch location for map-based history view.
    TODO: Add trade_available boolean for future creature trading feature.
    """
    __tablename__ = "caught_creatures"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creature_id = Column(Integer, ForeignKey("creatures.id"), nullable=False)
    caught_at = Column(DateTime, default=func.now(), nullable=False)

    owner = relationship("User", back_populates="caught_creatures")
    creature = relationship("Creature", back_populates="caught_instances")
