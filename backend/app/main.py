"""
FastAPI application entry point.

The app uses a lifespan context (from app.utils.spawn) to start the
background creature-spawn task on startup and cleanly cancel it on shutdown.

TODO: Wire in authentication middleware (JWT validation).
TODO: Add database migration check on startup (Alembic).
TODO: Add rate limiting and CORS restrictions for production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import creatures
from .utils.spawn import spawn_lifespan

# Create database tables (no-op if they already exist).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pokémon Go-like API",
    description="Backend API for the WAD Pokémon Go-like web application.",
    version="0.1.0",
    lifespan=spawn_lifespan,
)

# ---------------------------------------------------------------------------
# CORS – allow the React dev server during development.
# TODO: Restrict allowed_origins to the production domain before deployment.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(creatures.router)


@app.get("/", tags=["health"])
def root():
    """Health-check endpoint."""
    return {"status": "ok", "message": "Pokémon Go API is running"}
