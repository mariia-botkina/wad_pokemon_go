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
| Database   | PostgreSQL (SQLite for local dev)   |
| Map        | Leaflet.js + OpenStreetMap          |
| Auth       | JWT + OAuth (Google, Apple)         |
| Deployment | Docker, HTTPS (Nginx/Caddy)         |

## Directory Structure

```
wad_pokemon_go/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models.py            # ORM models (Creature, …)
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   └── creatures.py     # /creatures endpoints
│   │   └── utils/
│   │       ├── creature_generator.py  # Random creature factory
│   │       └── spawn.py               # In-memory spawn manager
│   ├── tests/
│   │   ├── test_spawn.py        # Unit tests for spawn logic
│   │   └── test_creatures_router.py   # API integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js               # Root component
│   │   ├── index.js             # React entry point
│   │   ├── api/
│   │   │   └── creatures.js     # API helper functions
│   │   └── components/
│   │       └── MapView.js       # Leaflet map + creature markers
│   ├── public/index.html
│   └── package.json
├── docs/
│   └── PLANNING.md
├── .gitignore
└── README.md
```

## How To Run

### Prerequisites

- Python 3.11+
- pip
- Docker (опционально, для контейнерного запуска)
- Git

### Backend (FastAPI)

#### Локальный запуск (рекомендуется для разработки)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу <http://localhost:8000>  
Swagger UI: <http://localhost:8000/docs>  
Проверка работоспособности:

```bash
curl http://localhost:8000/health
```

#### Запуск через Docker

```bash
cd backend
docker build -t pokemon-go-backend .
docker run -p 8000:8000 pokemon-go-backend
```

#### Тесты

```bash
cd backend
pytest tests/ -v
```

### Frontend

Frontend готов к локальному запуску из папки frontend.

**Response:**
```json
{"status":"ok"}
```

---

### `GET /creatures/nearby`

Returns a list of active, un-caught creatures within a given radius of the caller's location.

**Query Parameters**

| Parameter   | Type  | Required | Default | Description                          |
|-------------|-------|----------|---------|--------------------------------------|
| `lat`       | float | ✅        | –       | Caller's latitude (−90 … 90)         |
| `lon`       | float | ✅        | –       | Caller's longitude (−180 … 180)      |
| `radius_km` | float | ❌        | `0.5`   | Search radius in kilometres (≤ 50)   |

**Example request:**
```
GET /creatures/nearby?lat=48.8566&lon=2.3522&radius_km=0.5
```

**Example response:**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Pikachu",
    "type": "electric",
    "latitude": 48.8571,
    "longitude": 2.3530,
    "spawned_at": "2024-01-01T12:00:00+00:00",
    "expires_at": "2024-01-01T12:15:00+00:00",
    "is_caught": false
  }
]
```

**Side effect:** registers the caller's location so the background spawn task
continues to generate creatures in the same area.

---

### `POST /creatures/spawn` *(debug / admin)*

Manually trigger a batch of random creature spawns near a given location.

> ⚠️ This endpoint is intended for development and admin use only.  
> TODO: Gate behind an admin role once authentication is wired up.

**Query Parameters**

| Parameter   | Type  | Required | Default | Description                          |
|-------------|-------|----------|---------|--------------------------------------|
| `lat`       | float | ✅        | –       | Centre latitude                       |
| `lon`       | float | ✅        | –       | Centre longitude                      |
| `count`     | int   | ❌        | `5`     | Number of creatures to spawn (1–50)   |
| `radius_km` | float | ❌        | `0.5`   | Spawn radius in kilometres            |

**Example request:**
```
POST /creatures/spawn?lat=48.8566&lon=2.3522&count=3&radius_km=0.5
```

**Example response:**
```json
[
  {
    "id": "…",
    "name": "Charmander",
    "type": "fire",
    "latitude": 48.8569,
    "longitude": 2.3518,
    "spawned_at": "2024-01-01T12:00:00+00:00",
    "expires_at": "2024-01-01T12:15:00+00:00",
    "is_caught": false
  }
]
```

---

## Frontend Setup

### Requirements

- Node.js 18+

### Running locally

```bash
cd frontend
npm install
npm start
```

The app opens at `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

---

## Frontend Status

Frontend запускается локально командой `npm start` в папке `frontend`.

## License

MIT