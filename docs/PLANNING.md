# Specification: Location-based Creature Capture Web App

## 1. Overview

A web application accessible by link (no app store installation required) that mimics the main features of Pokémon Go:

- User account system (profile, authentication, authorization)
- Interactive map displaying the user's current location
- Randomized creature spawning on the map
- Catching creatures when nearby
- Collection/gallery of caught creatures
- Secure and privacy-aware implementation
- Easy sharing and onboarding (PWA or mobile-first web app)
- Admin debug mode for testing
- Modular system to add/generate new creatures

---

## 2. Functional Requirements

### 2.1 User Management

- **Sign Up / Login:** Users can create an account, log in, and manage their profile.
  - Support for third-party OAuth providers (Google, Apple) and email/password.
  - Email verification required.
- **Roles:**
  - Standard User
  - Admin/Debug user (extra controls & logs for testing)
- **Secure JWT** for session management.

### 2.2 Map & Location

- **Live Map:**
  - Interactive map (Leaflet.js + OpenStreetMap)
  - Displays user's current GPS location (uses mobile device geolocation with permission)
  - Map updates as user moves
- **Privacy:** User location is handled securely and not exposed to other users without consent.

### 2.3 Creature Spawning

- **Random Spawn:** Creatures spawn randomly around the map at defined intervals.
- **Spawn Logic (backend-validated):** Prevents client spoofing and ensures reasonable locations.
- **Despawn/Refresh Cycle:** Active spawns expire after a defined time window.

### 2.4 Catching Creatures

- **Proximity Check:** User can attempt to catch a creature only when within a distance threshold (e.g., 30 m).
- **Server-side Validation:** Prevents location spoofing; updates user's collection on success.

### 2.5 Creature Collection

- **Gallery:** Visual list of all captured creatures with details (stats, date/time captured, etc.).
- **Library:** Central database of all possible creatures.

### 2.6 Creature Generation & Library

- **Admin Module:** Add new creatures via form or API; generate random characteristics (name, type, stats, sprite).
- **User View:** Users only see creatures in the official library; no editing unless admin/debug mode.

### 2.7 Security & Sharing

- All critical game actions validated server-side.
- HTTPS only; input validation, rate limiting, brute-force protections.
- App shared as a link (mobile web / PWA).
- Consent screens for all location use.

---

## 3. Technical Stack

| Layer      | Technology                               |
|------------|------------------------------------------|
| Backend    | Python – FastAPI                         |
| Frontend   | React (mobile-first / PWA)               |
| Database   | PostgreSQL                               |
| Map        | Leaflet.js + OpenStreetMap               |
| Auth       | JWT + OAuth (Google, Apple)              |
| Real-time  | WebSockets (optional, for live spawns)   |
| Deployment | Docker, HTTPS (Nginx/Caddy), cloud host  |

---

## 4. Non-Functional Requirements

- **Scalable:** Supports future expansion (creature types, PVP, events).
- **Extensible:** Modular code for new creatures/mechanics.
- **Tested:** Unit and integration tests; debug/admin mode for manual testing.
- **Accessible:** Mobile accessibility standards (WCAG).
- **Documented:** Developer docs for extending the creature library and debugging.

---

## 5. Admin / Debug Mode

- Force creature spawns at arbitrary locations
- Force successful catches
- View/log all map events
- Add/edit/remove creatures in the library
- Bypass authorization (for testing only, gated by admin role)

---

## 6. Security Notes

- All critical game actions validated server-side.
- No critical data stored solely on the client.
- Regular audit logging on sensitive actions.
- Rate limiting and brute-force protections on auth endpoints.

---

## 7. Project To-Do List

### Step 1 – Project Setup ✅
- [x] Initialize repository
- [x] Create directory structure (`backend/`, `frontend/`, `docs/`)
- [x] Add `.gitignore` (Python, Node, editor)
- [x] Write initial `README.md`
- [x] Add `docs/PLANNING.md`

### Step 2 – Backend Skeleton
- [ ] Set up Python/FastAPI project in `backend/`
- [ ] Configure PostgreSQL connection
- [ ] User model and roles (user, admin)
- [ ] Registration, login, JWT auth endpoints
- [ ] OAuth integration (Google, Apple)

### Step 3 – Frontend Skeleton
- [ ] Set up React app in `frontend/`
- [ ] Mobile-first PWA configuration (manifest, icons)
- [ ] Basic routing (home, map, collection, login)

### Step 4 – Map & Geolocation
- [ ] Integrate Leaflet.js
- [ ] Display user's live GPS location
- [ ] Consent screen for location usage

### Step 5 – Creature System
- [ ] Creature data model (name, type, stats, sprite)
- [ ] Spawn logic (backend-driven, random locations, expiry)
- [ ] Catch endpoint with proximity validation

### Step 6 – Collection & Gallery
- [ ] User collection API endpoint
- [ ] Frontend gallery UI

### Step 7 – Admin & Debug Panel
- [ ] Admin-only routes (frontend + backend)
- [ ] Force spawn / force catch controls
- [ ] Creature library CRUD
- [ ] Event log viewer

### Step 8 – Creature Generation Module
- [ ] Admin form / API to add new creatures
- [ ] Random characteristic generator

### Step 9 – Testing
- [ ] Backend unit tests
- [ ] Frontend component tests
- [ ] Integration / E2E tests

### Step 10 – Deployment
- [ ] Dockerize backend and frontend
- [ ] HTTPS setup (Nginx/Caddy)
- [ ] Deploy to cloud (Render, Heroku, etc.)

---

## 8. Future Enhancements

- Creature evolution
- Battles/trades between users
- Social features (friends, chat)
- Global/regional events
- Achievements & leaderboards
