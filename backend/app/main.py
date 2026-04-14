"""
main.py - FastAPI application entry point.

Creates and configures the FastAPI app instance, registers routers,
sets up CORS middleware, and initializes the database on startup.

TODO: Add structured logging (e.g., structlog or loguru).
TODO: Add request ID middleware for tracing in production.
TODO: Configure CORS origins from environment variables for production security.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    On startup: creates all database tables defined in the ORM models
    (if they don't already exist). In production, prefer Alembic migrations.

    TODO: Replace create_all with Alembic-managed migrations in production.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Pokémon Go-like Web App API",
    description=(
        "Backend API for a location-based creature-capturing game. "
        "Provides authentication, user management, creature spawning, "
        "and collection endpoints."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS middleware
# Allow all origins in development. Restrict to specific domains in production.
# TODO: Load allowed origins from environment variable in production.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes defined in routes.py
app.include_router(router)


@app.get("/", summary="Health check")
def root():
    """
    Root health-check endpoint.

    Returns a simple message confirming the API is running.
    Useful for container orchestration health probes.
    """
    return {"message": "Pokémon Go API is running."}
