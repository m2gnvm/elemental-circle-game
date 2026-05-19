# Deployment

## Phase 1 — VPS + Coolify (Current Target)

[Coolify](https://coolify.io) is a self-hosted PaaS that runs on your VPS and handles
SSL (Let's Encrypt via Traefik), deployments from Git, environment variables, and
domain routing — no manual Nginx/Certbot configuration needed.

### One-time VPS setup

```bash
# Coolify one-liner installer (Ubuntu 22.04+ recommended)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Then open `http://<your-vps-ip>:8000` and follow the onboarding wizard.

---

### Domains

| Coolify app | Domain |
|---|---|
| Flutter UI | `elemental-circle.kamilstankowski.pl` |
| FastAPI backend | `ec-api.kamilstankowski.pl` |

Each service is a **separate Coolify application** pointing at the same Git repo
but a different Dockerfile. They are fully independent: separate deploys, logs,
and restarts. Postgres and Redis run as separate Coolify managed services.

---

### Infrastructure overview

```
Internet  HTTPS :443
  │
  ▼
Traefik (managed by Coolify)
  ├── elemental-circle.kamilstankowski.pl → [Coolify app: frontend]
  │     └── Nginx serving Flutter SPA (frontend/Dockerfile)
  │
  └── ec-api.kamilstankowski.pl          → [Coolify app: backend]
        └── FastAPI :8000 (root Dockerfile)

Managed services (internal, not public):
  elemental-postgres  (Coolify PostgreSQL)
  elemental-redis     (Coolify Redis)

Browser flow:
  Page load   → elemental-circle.kamilstankowski.pl        (Flutter JS/HTML)
  API calls   → ec-api.kamilstankowski.pl/api/v1/...       (FastAPI, CORS-OK)
  WebSocket   → wss://ec-api.kamilstankowski.pl/ws/...
```

---

### Step-by-step Coolify setup

#### 1. Create managed services (do this first)

- **Resources → New → PostgreSQL** — name it `elemental-postgres`
- **Resources → New → Redis** — name it `elemental-redis`

Copy their internal connection strings — you'll need them as env vars below.

#### 2. Create the Backend app

- **Resources → New → Application**
- Source: Git repo, branch `main`
- Build pack: **Dockerfile**
- Dockerfile path: `Dockerfile` (root)
- Domain: `ec-api.kamilstankowski.pl`

**Environment Variables:**

| Variable | Value |
|---|---|
| `DATABASE_URL` | *(from Coolify PostgreSQL → Connection)* |
| `REDIS_URL` | *(from Coolify Redis → Connection)* |
| `SECRET_KEY` | *(run: `python3 -c "import secrets; print(secrets.token_hex(32))"`)* |
| `ALLOWED_HOSTS` | `["https://elemental-circle.kamilstankowski.pl"]` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |

#### 3. Create the Frontend app

- **Resources → New → Application**
- Source: same Git repo, branch `main`
- Build pack: **Dockerfile**
- Dockerfile path: `frontend/Dockerfile`
- Docker build context: `frontend`
- Domain: `elemental-circle.kamilstankowski.pl`

**Build Arguments** (set in Coolify's Build Args / Environment Variables UI):

| Variable | Value |
|---|---|
| `API_URL` | `https://ec-api.kamilstankowski.pl` |
| `API_WS_URL` | `wss://ec-api.kamilstankowski.pl` |

> **These are build-time args, not runtime env vars.**  
> In Coolify look for "Build Arguments" or set them as env vars marked
> as "Available during build". Flutter bakes them into the JS bundle at
> compile time — if you change the domain you must **Rebuild**, not just Restart.

#### 4. Deploy order

1. Deploy backend first (it needs DB/Redis to be healthy)
2. Deploy frontend after (it just serves static files, no runtime deps)

#### 5. Verify

```
https://elemental-circle.kamilstankowski.pl          → Flutter web UI
https://ec-api.kamilstankowski.pl/health             → {"status":"healthy"}
https://ec-api.kamilstankowski.pl/api/v1/docs        → Swagger UI
```

---

### docker-compose.yml — local dev only

The `docker-compose.yml` in the repo is kept for running the full stack locally.
In production, Coolify manages each service separately.

```bash
# Local dev — copy and fill in .env.example first
cp .env.example .env
docker compose up --build
```

---

### Keeping secrets out of Git

- `.env` is gitignored — never commit it.
- All production secrets live only in Coolify's encrypted env var store.

---

### Providers (where to run Coolify)
- Hetzner CX22 (2 vCPU, 4 GB) — recommended for this stack
- OVH VPS SSD
- Scaleway DEV1-S

---

## Phase 2 — AWS (Future)

| AWS Service | Role |
|-------------|------|
| ECS Fargate | Container orchestration |
| RDS (PostgreSQL) | Managed database |
| ElastiCache (Redis) | Managed Redis |
| S3 | Static assets, replay archives |
| CloudWatch | Logs, metrics |
| ECR | Container registry |
| ALB | Load balancer |

Deployment scripts: `deploy/aws-deploy.sh`

---

## Phase 2 — Azure (Alternative)

Deployment scripts: `deploy/azure-deploy.sh`

---

## Kubernetes (Experimental)

Basic K8s manifests in `k8s/`:
- `namespace.yaml`
- `postgres-deployment.yaml`

Not used in production yet — exploratory only.

---

## Environment Secrets

Never commit `.env` to the repo. Use:
- VPS: `.env` file on server, restricted permissions
- AWS: Secrets Manager or SSM Parameter Store
- Docker: environment variables in compose override file

---

## CI/CD (Phase 2)

Planned:
- GitHub Actions workflow on `main` push
- Build & push Docker image to ECR
- Deploy to ECS via `aws ecs update-service`
