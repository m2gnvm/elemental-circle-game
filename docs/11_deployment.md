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

| Service | Domain |
|---|---|
| Flutter UI (`frontend`) | `elemental-circle.kamilstankowski.pl` |
| FastAPI backend (`app`) | `ec-api.kamilstankowski.pl` |

Both services live in the same Docker Compose stack on the same VPS.
Coolify's built-in Traefik reverse proxy handles TLS and routes each domain to
the correct container.

---

### Deploying the full stack in Coolify

#### 1. Create a new Resource → Docker Compose

- Source: your Git repo (GitHub / GitLab / self-hosted Gitea)
- Docker Compose file: `docker-compose.yml` (root of repo)
- Branch: `main`

#### 2. Assign domains to services

In Coolify's **Domains** tab, set:

| Service name | Domain |
|---|---|
| `frontend` | `elemental-circle.kamilstankowski.pl` |
| `app` | `ec-api.kamilstankowski.pl` |

Coolify provisions TLS certificates automatically via Let's Encrypt.

#### 3. Set Environment Variables in Coolify UI

Go to **Environment Variables** for the resource and add:

| Variable | Value | Purpose |
|---|---|---|
| `API_URL` | `https://ec-api.kamilstankowski.pl` | Baked into Flutter build — where the browser calls |
| `API_WS_URL` | `wss://ec-api.kamilstankowski.pl` | WebSocket equivalent |
| `ALLOWED_ORIGINS` | `["https://elemental-circle.kamilstankowski.pl"]` | Backend CORS whitelist |
| `POSTGRES_PASSWORD` | *(strong random string)* | |
| `SECRET_KEY` | *(64-char hex, see below)* | |
| `POSTGRES_DB` | `elemental_circle` | |
| `POSTGRES_USER` | `gameuser` | |

Generate `SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 4. Deploy

Click **Deploy**. Coolify will:
1. Build the backend image (`Dockerfile` in repo root)
2. Build the Flutter web image (`frontend/Dockerfile`) — ~5-10 min first time
3. Start postgres → redis → app → frontend in dependency order
4. Provision TLS certs and start routing traffic

#### 5. Verify

```
https://elemental-circle.kamilstankowski.pl          → Flutter web UI
https://ec-api.kamilstankowski.pl/health             → FastAPI health check
https://ec-api.kamilstankowski.pl/api/v1/docs        → Swagger UI
```

---

### Architecture on the VPS

```
Internet
  │  HTTPS :443
  ▼
Traefik (managed by Coolify)
  ├── elemental-circle.kamilstankowski.pl
  │     └── elemental_frontend  (Nginx serving Flutter SPA)
  │
  └── ec-api.kamilstankowski.pl
        └── elemental_app  (FastAPI :8000)

Browser flow:
  Page load   → elemental-circle.kamilstankowski.pl  (Flutter JS/HTML)
  API calls   → ec-api.kamilstankowski.pl/api/v1/...  (FastAPI, CORS-whitelisted)
  WebSocket   → wss://ec-api.kamilstankowski.pl/ws/...
```

Postgres and Redis are **internal only** — not exposed to the internet.

> **Important — Flutter bakes the URL at image build time.**  
> If you ever change `API_URL`, trigger a **Rebuild & Deploy** (not just Restart)
> so the Flutter web assets are recompiled with the new value.

---

### Keeping secrets out of Git

- `.env` is gitignored — never commit it.
- Copy `.env.example` → `.env` locally for `docker compose up` in dev.
- All production secrets live only in Coolify's encrypted environment variable store.

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
