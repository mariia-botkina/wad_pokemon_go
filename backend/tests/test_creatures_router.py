"""
Integration tests for the /creatures API router.

Uses FastAPI's TestClient (httpx) to exercise the endpoints end-to-end
without requiring a live database or external services.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_nearby_returns_list():
    """GET /creatures/nearby must return a JSON array."""
    response = client.get("/creatures/nearby", params={"lat": 48.8566, "lon": 2.3522})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_nearby_response_schema():
    """Each creature in the response must have the expected fields."""
    response = client.get("/creatures/nearby", params={"lat": 48.8566, "lon": 2.3522})
    assert response.status_code == 200
    for creature in response.json():
        assert "id" in creature
        assert "name" in creature
        assert "type" in creature
        assert "latitude" in creature
        assert "longitude" in creature
        assert "spawned_at" in creature
        assert "is_caught" in creature


def test_nearby_missing_lat_returns_422():
    """Missing required query param should return 422 Unprocessable Entity."""
    response = client.get("/creatures/nearby", params={"lon": 2.3522})
    assert response.status_code == 422


def test_spawn_endpoint_returns_creatures():
    """POST /creatures/spawn must return the requested number of creatures."""
    response = client.post(
        "/creatures/spawn",
        params={"lat": 48.8566, "lon": 2.3522, "count": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_spawn_creature_fields():
    """Spawned creatures must have valid coordinates and not be caught."""
    response = client.post(
        "/creatures/spawn",
        params={"lat": 0.0, "lon": 0.0, "count": 1, "radius_km": 0.5},
    )
    assert response.status_code == 200
    creature = response.json()[0]
    assert -90 <= creature["latitude"] <= 90
    assert -180 <= creature["longitude"] <= 180
    assert creature["is_caught"] is False
