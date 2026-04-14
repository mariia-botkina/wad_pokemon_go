"""
Tests for the creature spawn logic.

Covers:
  - generate_creature: random location, correct schema, lifespan
  - haversine_km: known distances
  - SpawnManager: spawn_batch, get_active, tick, register_location
"""

import math
from datetime import datetime, timedelta, timezone

import pytest

from app.utils.creature_generator import (
    CREATURE_TEMPLATES,
    generate_creature,
)
from app.utils.spawn import SpawnManager, haversine_km


# ---------------------------------------------------------------------------
# haversine_km
# ---------------------------------------------------------------------------


def test_haversine_same_point():
    """Distance from a point to itself must be zero."""
    assert haversine_km(48.8566, 2.3522, 48.8566, 2.3522) == pytest.approx(0.0)


def test_haversine_paris_london():
    """Paris → London is approximately 341 km."""
    dist = haversine_km(48.8566, 2.3522, 51.5074, -0.1278)
    assert 330 < dist < 350


# ---------------------------------------------------------------------------
# generate_creature
# ---------------------------------------------------------------------------


def test_generate_creature_returns_correct_schema():
    """generate_creature returns a CreatureCreate with valid fields."""
    creature = generate_creature(lat=48.8566, lon=2.3522, radius_km=0.5)
    assert creature.name in [t["name"] for t in CREATURE_TEMPLATES]
    assert creature.type in [t["type"] for t in CREATURE_TEMPLATES]
    assert -90 <= creature.latitude <= 90
    assert -180 <= creature.longitude <= 180


def test_generate_creature_within_radius():
    """The spawn point must be within the requested radius."""
    origin_lat, origin_lon = 48.8566, 2.3522
    radius_km = 0.3

    for _ in range(50):  # Statistical check over multiple samples.
        c = generate_creature(lat=origin_lat, lon=origin_lon, radius_km=radius_km)
        dist = haversine_km(origin_lat, origin_lon, c.latitude, c.longitude)
        # Allow a small tolerance for floating-point rounding.
        assert dist <= radius_km * 1.5, f"Creature spawned {dist:.3f} km away (limit {radius_km} km)"


def test_generate_creature_has_expiry():
    """By default creatures have an expires_at set ~15 minutes in the future."""
    creature = generate_creature(lat=0.0, lon=0.0, lifespan_minutes=15)
    assert creature.expires_at is not None
    delta = creature.expires_at - datetime.now(timezone.utc)
    assert timedelta(minutes=14) < delta < timedelta(minutes=16)


def test_generate_creature_no_expiry():
    """Passing lifespan_minutes=None produces no expiry."""
    creature = generate_creature(lat=0.0, lon=0.0, lifespan_minutes=None)
    assert creature.expires_at is None


# ---------------------------------------------------------------------------
# SpawnManager
# ---------------------------------------------------------------------------


def test_spawn_batch_creates_creatures():
    manager = SpawnManager()
    creatures = manager.spawn_batch(lat=48.8566, lon=2.3522, count=3, radius_km=0.5)
    assert len(creatures) == 3
    assert all(c.is_caught is False for c in creatures)
    assert len(manager._creatures) == 3


def test_get_active_returns_nearby_creatures():
    manager = SpawnManager()
    manager.spawn_batch(lat=48.8566, lon=2.3522, count=5, radius_km=0.5)
    nearby = manager.get_active(lat=48.8566, lon=2.3522, radius_km=1.0)
    assert len(nearby) >= 1


def test_get_active_excludes_distant_creatures():
    """Creatures spawned far from the query point must not be returned."""
    manager = SpawnManager()
    # Spawn near Paris.
    manager.spawn_batch(lat=48.8566, lon=2.3522, count=5, radius_km=0.1)
    # Query from London (≈ 341 km away).
    nearby = manager.get_active(lat=51.5074, lon=-0.1278, radius_km=1.0)
    assert nearby == []


def test_tick_removes_expired_creatures():
    """tick() must remove creatures whose expires_at is in the past."""
    manager = SpawnManager()
    creatures = manager.spawn_batch(lat=0.0, lon=0.0, count=3, radius_km=0.1)
    # Manually expire all creatures.
    for c in creatures:
        c.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    removed = manager.tick()
    assert removed == 3
    assert len(manager._creatures) == 0


def test_get_active_excludes_expired():
    """get_active() must not return creatures that have already expired."""
    manager = SpawnManager()
    creatures = manager.spawn_batch(lat=0.0, lon=0.0, count=2, radius_km=0.1)
    for c in creatures:
        c.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    active = manager.get_active(lat=0.0, lon=0.0, radius_km=1.0)
    assert active == []


def test_register_location_updates_state():
    manager = SpawnManager()
    manager.register_location(10.0, 20.0)
    assert manager._last_lat == 10.0
    assert manager._last_lon == 20.0
