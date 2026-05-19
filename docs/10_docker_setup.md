# Docker Setup

## Services

### `docker-compose.yml` (development)

| Container | Image | Purpose |
|-----------|-------|---------|
| `backend` | local Dockerfile | FastAPI app |
| `postgres` | postgres:15 | Persistent storage |
| `redis` | redis:7 | Live game state, sessions |
| `nginx` | nginx:alpine | Reverse proxy / SSL termination |

### `docker-compose.prod.yml` (production override)

Extends the base compose with production-specific settings (env vars, restart policies, volume mounts).

---

## Dockerfile

The backend `Dockerfile` builds the Python app:

1. Base image: `python:3.11-slim`
2. Copies `requirements.txt` and installs dependencies
3. Copies app code
4. Runs `uvicorn app.main:app`

---

## Networking

All services share a Docker network. The backend reaches Postgres and Redis by service name:

```
DATABASE_URL=postgresql://user:pass@postgres:5432/elemental
REDIS_URL=redis://redis:6379
```

Nginx proxies `80/443` → `backend:8000`.

---

## Volume Mounts

| Volume | Purpose |
|--------|---------|
| `postgres_data` | Persistent DB across restarts |
| `./app:/app/app` | Hot reload in dev (code changes reflect immediately) |

---

## Goals

- Reproducible local development environment
- Simple single-command onboarding (`docker compose up`)
- Isolated services with clear networking
- Easy teardown and reset (`docker compose down -v`)

---

## Future Containers (Phase 3+)

| Container | Purpose |
|-----------|---------|
| `redpanda` | Kafka-compatible event streaming |
| `spark` | Batch / streaming analytics |
| `grafana` | Metrics dashboards |
| `prometheus` | Metrics scraping |
| `mlflow` | Model tracking |

---

## Deployment Files

```
deploy/
├── aws-deploy.sh     # ECS / ECR deployment script
└── azure-deploy.sh   # Azure Container Apps script

k8s/
├── namespace.yaml
└── postgres-deployment.yaml
```

See `docs/11_deployment.md` for deployment strategy.
