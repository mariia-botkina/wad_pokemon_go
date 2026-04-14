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
2. See [`docs/PLANNING.md`](docs/PLANNING.md) for the full specification and development plan.

---

## Backend Setup (FastAPI + PostgreSQL)

### Prerequisites

- Python 3.11+
- PostgreSQL server running locally (or via Docker)

### 1. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/pokemon_go_db
SECRET_KEY=replace-with-a-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure `SECRET_KEY` with:

```bash
openssl rand -hex 32
```

### 3. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE pokemon_go_db;"
```

### 4. Run database migrations (Alembic)

Initialize Alembic (first time only):

```bash
cd backend
alembic init alembic
```

Update `alembic/env.py` to import your models and use the `DATABASE_URL` from your `.env`.  
Then generate and apply the initial migration:

```bash
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

> **Note:** If you skip Alembic, the app will auto-create tables on startup using `Base.metadata.create_all()`.  
> This is convenient for development but not recommended for production.

### 5. Start the backend server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

---

## Authentication API

### Register a new user

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "player@example.com", "password": "securepassword"}'
```

**Response:**
```json
{
  "id": 1,
  "email": "player@example.com",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Login and receive a JWT token

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "player@example.com", "password": "securepassword"}'
```

**Response:**
```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

### Access a protected endpoint

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <jwt-token>"
```

---

## License

MIT