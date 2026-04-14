/**
 * creatures.js – API helpers for the /creatures endpoints.
 *
 * All functions communicate with the FastAPI backend.  The base URL defaults
 * to the CRA proxy (http://localhost:8000) in development; override via the
 * REACT_APP_API_URL environment variable for staging/production deployments.
 *
 * TODO: Add authentication headers (Bearer token) once JWT login is wired up.
 * TODO: Add retry/exponential-backoff for network errors.
 */

const API_BASE = process.env.REACT_APP_API_URL || "";

/**
 * Fetch creatures near the given coordinates.
 *
 * @param {number} lat       - User's latitude
 * @param {number} lon       - User's longitude
 * @param {number} radiusKm  - Search radius in kilometres (default 0.5)
 * @returns {Promise<Array>} - Array of creature objects from the API
 */
export async function fetchNearbyCreatures(lat, lon, radiusKm = 0.5) {
  const url = new URL(`${API_BASE}/creatures/nearby`, window.location.origin);
  url.searchParams.set("lat", lat);
  url.searchParams.set("lon", lon);
  url.searchParams.set("radius_km", radiusKm);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Failed to fetch nearby creatures: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Trigger a manual spawn batch near the given location (admin/debug use).
 *
 * TODO: Gate behind admin auth check in the UI once roles are implemented.
 *
 * @param {number} lat      - Centre latitude
 * @param {number} lon      - Centre longitude
 * @param {number} count    - Number of creatures to spawn (default 5)
 * @param {number} radiusKm - Spawn radius in kilometres (default 0.5)
 * @returns {Promise<Array>} - Array of newly spawned creature objects
 */
export async function spawnCreatures(lat, lon, count = 5, radiusKm = 0.5) {
  const url = new URL(`${API_BASE}/creatures/spawn`, window.location.origin);
  url.searchParams.set("lat", lat);
  url.searchParams.set("lon", lon);
  url.searchParams.set("count", count);
  url.searchParams.set("radius_km", radiusKm);

  const response = await fetch(url.toString(), { method: "POST" });
  if (!response.ok) {
    throw new Error(`Failed to spawn creatures: ${response.statusText}`);
  }
  return response.json();
}
