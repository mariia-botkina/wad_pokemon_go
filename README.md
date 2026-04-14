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
3. Backend and frontend setup instructions will be added as each component is scaffolded.

## License

MIT