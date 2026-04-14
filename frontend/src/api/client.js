/**
 * API client helpers.
 *
 * All requests are sent to /api/* which Vite's dev-server proxy forwards to
 * the FastAPI backend at http://localhost:8000.
 *
 * In production, set VITE_API_BASE_URL to the deployed backend URL.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

/** Read the stored JWT token from localStorage. */
function getToken() {
  return localStorage.getItem('token')
}

/** Build headers including Authorization if a token is present. */
function authHeaders(extra = {}) {
  const token = getToken()
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  }
}

/** Generic fetch wrapper that throws on non-2xx status. */
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

// ── Auth ───────────────────────────────────────────────────────────────────

/** Register a new account; returns { access_token, token_type }. */
export async function register(username, email, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ username, email, password }),
  })
}

/** Login with username + password; returns { access_token, token_type }. */
export async function login(username, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ username, password }),
  })
}

/** Return the profile of the currently authenticated user. */
export async function getMe() {
  return apiFetch('/auth/me', { headers: authHeaders() })
}

// ── Creatures ──────────────────────────────────────────────────────────────

/**
 * Fetch spawned creatures near the given GPS position.
 * @param {number} latitude
 * @param {number} longitude
 * @param {number} [radiusMetres=500]
 */
export async function getNearbyCreatures(latitude, longitude, radiusMetres = 500) {
  const params = new URLSearchParams({ latitude, longitude, radius_metres: radiusMetres })
  return apiFetch(`/creatures/nearby?${params}`, { headers: authHeaders() })
}

/**
 * Manually spawn a creature near the user (for demo / testing).
 * @param {number} latitude
 * @param {number} longitude
 */
export async function spawnCreature(latitude, longitude) {
  const params = new URLSearchParams({ latitude, longitude })
  return apiFetch(`/creatures/spawn?${params}`, {
    method: 'POST',
    headers: authHeaders(),
  })
}

/**
 * Attempt to catch a spawned creature.
 * @param {number} spawnedCreatureId
 * @param {number} userLatitude
 * @param {number} userLongitude
 * @returns {{ success: boolean, message: string, caught_creature_id?: number }}
 */
export async function catchCreature(spawnedCreatureId, userLatitude, userLongitude) {
  return apiFetch('/creatures/catch', {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({
      spawned_creature_id: spawnedCreatureId,
      user_latitude: userLatitude,
      user_longitude: userLongitude,
    }),
  })
}

// ── Collection ─────────────────────────────────────────────────────────────

/**
 * Fetch the authenticated user's collection (caught creatures).
 * Ordered newest-to-oldest.
 * @returns {{ total: number, items: CaughtCreature[] }}
 */
export async function getMyCollection() {
  return apiFetch('/users/me/collection', { headers: authHeaders() })
}
