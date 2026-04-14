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

## Local Development Setup

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js (v18+ recommended)](https://nodejs.org/)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [PostgreSQL](https://www.postgresql.org/) (required for persistent storage)

---

### 1. Clone the Repository

```bash
git clone https://github.com/mariia-botkina/wad_pokemon_go.git
cd wad_pokemon_go
```

---

### 2. Backend Setup (FastAPI)

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example environment file and fill in your values
cp .env.example .env

# Start the development server (auto-reload on code changes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at <http://localhost:8000>.  
Interactive docs (Swagger UI) are at <http://localhost:8000/docs>.  
Health-check endpoint: `GET /health`

#### Run backend with Docker

```bash
cd backend
docker build -t pokemon-go-backend .
docker run -p 8000:8000 pokemon-go-backend
```

---

### 3. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install        # or: yarn

# Start the development server
npm start          # or: yarn start
```

The frontend will be available at <http://localhost:3000>.

---

### 4. Environment Variables

**Backend** (`backend/.env`):

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql://user:password@localhost:5432/pokemon_go` |
| `SECRET_KEY` | Secret key used for signing JWT tokens |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth credentials for Google login |

**Frontend** (`frontend/.env` or `frontend/src/config.js`):

| Variable | Description |
|---|---|
| `REACT_APP_API_URL` | Base URL for backend API, e.g. `http://localhost:8000` |

---

### 5. Useful Scripts

**Backend tests:**

```bash
cd backend
pytest
```

**Frontend lint:**

```bash
cd frontend
npm run lint       # or: yarn lint
```

---

### 6. Common Issues

- **Port conflicts:** Make sure ports `8000` (backend) and `3000` (frontend) are not already in use.
- **Python version:** Ensure you are using Python 3.9 or higher (`python --version`).
- **Node version:** Ensure you are using Node.js v18 or higher (`node --version`).
- **Missing dependencies:** If you hit import errors, re-run `pip install -r requirements.txt` (backend) or `npm install` (frontend).
- **Database connection:** Double-check `DATABASE_URL` in `backend/.env` and that your PostgreSQL instance is running.
- **Database migrations:** Run `alembic upgrade head` inside the `backend/` directory to apply the latest migrations.

---

### 7. Demo Data & First Steps

- The backend may seed demo creatures into the database on first run (see backend startup logs).
- Open your browser at <http://localhost:3000> and allow location access to start playing.
- Use the admin panel (requires admin role) to force creature spawns during development.

---

### 8. Contribution

Pull requests, issues, and ideas are very welcome!  
See [`docs/PLANNING.md`](docs/PLANNING.md) for the full specification and development roadmap.

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/mariia-botkina/wad_pokemon_go.git
   cd wad_pokemon_go
   ```
2. See [`docs/PLANNING.md`](docs/PLANNING.md) for the full specification and development plan.
3. Backend and frontend setup instructions will be added as each component is scaffolded.

## License

MIT