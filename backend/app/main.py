@app.get("/", tags=["info"])
async def root():
    """Welcome endpoint for root URL."""
    return {
        "message": "Welcome to the Pokémon Go-like API!",
        "docs_url": "/docs"
    }
"""
main.py – FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Pokémon Go-like Web App API",
    description="Backend API for a location-based creature-capturing game.",
    version="0.1.0",
)

# Include API routes
app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health-check endpoint – returns a simple status message."""
    return {"status": "ok"}


# Новый endpoint для получения версии API
@app.get("/version", tags=["info"])
async def version() -> dict:
    """Returns the current API version."""
    return {"version": app.version}
