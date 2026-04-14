# Pokémon Go-like Web App (WAD Project)

A location-based creature-capturing game playable via mobile browser.

## Features

- User authentication and profiles (JWT-based, with OAuth support)
- Real-time interactive map with the user's current GPS location
- Creatures spawning randomly on the map
- Catch nearby creatures with server-side proximity validation
- Collection/gallery of captured creatures
- Admin/debug mode for testing and creature management
- Extensible creature library (add/generate new creatures via admin module)
- Secure, mobile-first, shareable as a link (PWA-ready)

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python – FastAPI                    |
| Frontend   | React (mobile-first / PWA)          |
| Database   | PostgreSQL                          |
| Map        | Leaflet.js + OpenStreetMap          |
| Auth       | JWT + OAuth (Google, Apple)         |
| Deployment | Docker, HTTPS (Nginx/Caddy)         |

## Directory Structure

```
wad_pokemon_go/
├── backend/        # Python FastAPI application (API, auth, game logic)
├── frontend/       # React frontend (map, UI, PWA)
├── docs/           # Project documentation and planning
├── .gitignore
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/mariia-botkina/wad_pokemon_go.git
   cd wad_pokemon_go
   ```

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Interactive API docs will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The backend uses SQLite by default (`backend/pokemon_go.db`). Replace `DATABASE_URL`
in `backend/database.py` with a PostgreSQL URL for production.

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev      # starts on http://localhost:3000
```

The Vite dev server automatically proxies `/api/*` requests to `http://localhost:8000`.

---

## API Reference

All API endpoints are prefixed with the backend base URL (default: `http://localhost:8000`).
Protected routes require a Bearer JWT obtained from `/auth/register` or `/auth/login`.

### Authentication

| Method | Endpoint           | Auth | Description                              |
|--------|--------------------|------|------------------------------------------|
| POST   | `/auth/register`   | –    | Create a new account; returns JWT        |
| POST   | `/auth/login`      | –    | Exchange credentials for a JWT           |
| GET    | `/auth/me`         | JWT  | Return the current user's profile        |

**Register example:**
```http
POST /auth/register
Content-Type: application/json

{ "username": "trainer123", "email": "trainer@example.com", "password": "secret" }
```
Response `201 Created`:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### Creatures

| Method | Endpoint              | Auth | Description                                           |
|--------|-----------------------|------|-------------------------------------------------------|
| GET    | `/creatures/nearby`   | –    | List active spawns near a GPS position                |
| POST   | `/creatures/spawn`    | JWT  | Manually spawn a creature (demo/debug)                |
| POST   | `/creatures/catch`    | JWT  | Attempt to catch a spawned creature (proximity check) |

**Nearby creatures:**
```http
GET /creatures/nearby?latitude=51.5074&longitude=-0.1278&radius_metres=500
```
Response `200 OK`:
```json
[
  {
    "id": 1,
    "creature_id": 3,
    "latitude": 51.508,
    "longitude": -0.125,
    "spawned_at": "2024-01-15T14:00:00Z",
    "expires_at": "2024-01-15T14:10:00Z",
    "creature": { "id": 3, "name": "Flamara", "creature_type": "fire", "base_power": 75, "description": "..." }
  }
]
```

**Catch a creature:**
```http
POST /creatures/catch
Authorization: Bearer <token>
Content-Type: application/json

{ "spawned_creature_id": 1, "user_latitude": 51.5074, "user_longitude": -0.1278 }
```
Response `200 OK`:
```json
{ "success": true, "message": "Caught!", "caught_creature_id": 5 }
```

---

### User Collection

| Method | Endpoint                  | Auth | Description                                          |
|--------|---------------------------|------|------------------------------------------------------|
| GET    | `/users/me/collection`    | JWT  | Return the authenticated user's caught creatures     |

The collection is ordered **newest-to-oldest** by the `caught_at` timestamp.

**Request:**
```http
GET /users/me/collection
Authorization: Bearer <token>
```

**Response `200 OK`:**
```json
{
  "total": 2,
  "items": [
    {
      "id": 5,
      "caught_at": "2024-01-15T14:32:00Z",
      "creature": {
        "id": 3,
        "name": "Flamara",
        "creature_type": "fire",
        "base_power": 75,
        "description": "A fierce fire creature born from volcanic eruptions."
      }
    },
    {
      "id": 3,
      "caught_at": "2024-01-15T13:10:00Z",
      "creature": {
        "id": 7,
        "name": "Icewhisp",
        "creature_type": "ice",
        "base_power": 62,
        "description": "An icy creature that leaves frost wherever it walks."
      }
    }
  ]
}
```

**Error responses:**
- `401 Unauthorized` – missing or invalid JWT.

---

## Directory Structure

```
wad_pokemon_go/
├── backend/
│   ├── main.py          # FastAPI app entry point, startup seed
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # ORM models (User, Creature, SpawnedCreature, CaughtCreature)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # JWT creation/verification, password hashing
│   ├── requirements.txt
│   └── routers/
│       ├── auth.py      # POST /auth/register, POST /auth/login, GET /auth/me
│       ├── creatures.py # GET /creatures/nearby, POST /creatures/spawn, POST /creatures/catch
│       └── users.py     # GET /users/me/collection
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx      # Root component, auth state, routing
│       ├── api/
│       │   └── client.js   # API helper functions
│       ├── components/
│       │   └── Navbar.jsx  # Navigation bar (Map ↔ Collection links)
│       └── pages/
│           ├── LoginPage.jsx      # Login / register form
│           ├── MapPage.jsx        # Leaflet map, spawn markers, catch dialog
│           └── CollectionPage.jsx # Gallery of caught creatures
├── docs/
│   └── PLANNING.md
├── .gitignore
└── README.md
```

## License

MIT