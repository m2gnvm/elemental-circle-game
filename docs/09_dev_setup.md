# Development Setup

## Requirements

- Docker 24+
- Docker Compose v2
- Python 3.11+
- Git

Optional (for frontend work):
- Flutter SDK

---

## Quick Start (Docker)

The fastest way to get the full stack running:

```bash
docker compose up
```

This starts: `backend`, `postgres`, `redis`, `nginx`.

API available at `http://localhost:8000`.
Swagger UI at `http://localhost:8000/docs`.

---

## Backend (local, without Docker)

```bash
# Create virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit env
cp env.example .env
# Set DATABASE_URL, REDIS_URL, SECRET_KEY in .env

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requires PostgreSQL and Redis to be reachable (use Docker for those):

```bash
docker compose up postgres redis
```

---

## Environment Variables

See `env.example` for all variables. Key ones:

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://user:pass@localhost/elemental` | |
| `REDIS_URL` | `redis://localhost:6379` | |
| `SECRET_KEY` | `<random 32+ chars>` | JWT signing key |
| `ALLOWED_HOSTS` | `["*"]` | CORS origins (JSON list) |

---

## Verify Setup

```bash
curl http://localhost:8000/health
# → {"status": "healthy"}

curl http://localhost:8000/
# → {"message": "Elemental Circle Game API", "version": "1.0.0"}
```

---

## Test Scripts

Interactive test scripts are in `test_scripts/`:

```bash
python test_scripts/interactive_game.py    # Manual two-player CLI session
python test_scripts/simulate_ai_fights.py  # Automated AI vs AI simulation
```

---

## Useful Commands

```bash
# Rebuild after code changes
docker compose up --build

# Reset database (destroys all data)
docker compose down -v && docker compose up

# View logs
docker compose logs -f backend

# Check health
bash check_docker_health.sh
```
