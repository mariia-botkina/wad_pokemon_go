"""Tests for FastAPI lifespan wiring and background spawn task lifecycle."""

import asyncio
import threading

from fastapi.testclient import TestClient

from app.main import app
from app.utils import spawn as spawn_module


def test_spawn_lifespan_starts_and_cancels_background_task(monkeypatch):
    """The lifespan handler should start and cancel the background spawn task."""
    started = threading.Event()
    cancelled = threading.Event()

    async def fake_auto_spawn_loop(*args, **kwargs):  # noqa: ARG001
        started.set()
        try:
            # Block forever until cancellation so shutdown path is exercised.
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    monkeypatch.setattr(spawn_module.spawn_manager, "auto_spawn_loop", fake_auto_spawn_loop)

    with TestClient(app) as client:
        assert started.wait(timeout=1.0)
        response = client.get("/health")
        assert response.status_code == 200

    assert cancelled.wait(timeout=1.0)
