"""
Main FastAPI application entry point.

Mounts all routers and sets up the database on startup.
Seeds a small default creature library if the database is empty.

Run locally with:
  uvicorn main:app --reload --port 8000

Interactive API docs available at:
  http://localhost:8000/docs   (Swagger UI)
  http://localhost:8000/redoc  (ReDoc)
"""

from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, SessionLocal, engine
from routers import auth, creatures, users

# ── Create all database tables ────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Pokémon Go-like Web App API",
    description=(
        "Backend API for a location-based creature-capturing game.\n\n"
        "Authentication uses JWT Bearer tokens. Obtain a token via "
        "`POST /auth/register` or `POST /auth/login`, then include it in "
        "the `Authorization: Bearer <token>` header for protected routes."
    ),
    version="0.1.0",
)

# ── CORS – allow the React dev server to call the API ─────────────────────────
# TODO: Restrict origins to the production domain before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ─────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(creatures.router)
app.include_router(users.router)


# ── Database seed ─────────────────────────────────────────────────────────────
def _seed_creatures():
    """
    Populate the creature library with a default set of creatures if it is empty.

    This runs once on startup and is skipped if creatures already exist.
    In production, manage creatures via the admin API instead.
    """
    db = SessionLocal()
    try:
        if db.query(models.Creature).count() > 0:
            return  # Already seeded

        default_creatures = [
            models.Creature(name="Flamara",   creature_type="fire",    base_power=75, description="A fierce fire creature born from volcanic eruptions."),
            models.Creature(name="Aquafin",   creature_type="water",   base_power=60, description="A swift water creature that glides through rivers."),
            models.Creature(name="Leafeon",   creature_type="grass",   base_power=55, description="A gentle grass creature that thrives in sunlit forests."),
            models.Creature(name="Voltail",   creature_type="electric",base_power=80, description="An electric creature that crackles with static energy."),
            models.Creature(name="Rockhorn",  creature_type="rock",    base_power=70, description="A sturdy rock creature with an indestructible hide."),
            models.Creature(name="Ghostmist", creature_type="ghost",   base_power=65, description="A mysterious ghost creature that fades in and out of sight."),
            models.Creature(name="Icewhisp",  creature_type="ice",     base_power=62, description="An icy creature that leaves frost wherever it walks."),
            models.Creature(name="Psyray",    creature_type="psychic", base_power=85, description="A psychic creature that reads minds and bends space."),
        ]
        db.add_all(default_creatures)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    """Run startup tasks: seed the creature library."""
    _seed_creatures()


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def health_check():
    """Simple health-check endpoint – returns OK if the server is running."""
    return {"status": "ok", "message": "Pokémon Go-like API is running"}
