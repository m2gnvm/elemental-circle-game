# Roadmap

## Phase 1 — Core Multiplayer (Complete)

- [x] JWT authentication (register / login)
- [x] Game create / join / start via REST
- [x] Card play with elemental battle resolution
- [x] Redis-backed live game state (`HybridGameService`)
- [x] WebSocket room broadcast
- [x] PostgreSQL persistence (users, games, events)
- [x] Docker Compose environment
- [x] Godot API reference docs (usable for Flutter too)

---

## Phase 2 — Architecture Hardening

- [ ] Extract pure `GameEngine` class (no DB, no HTTP, fully deterministic)
- [ ] Wire WebSocket push after game mutations (`broadcast_game_state`)
- [ ] JWT validation on WebSocket connect
- [ ] Migrate SQLAlchemy to `AsyncSession`
- [ ] Deck building system (user-owned decks)
- [ ] Replay system from `game_events` log
- [ ] pytest suite — unit + integration
- [ ] CI pipeline (GitHub Actions)
- [ ] Cleaner error handling (structured FastAPI exception handlers)

---

## Phase 3 — Telemetry & Streaming

- [ ] Redpanda container in Docker Compose
- [ ] `EventService` publishes to Redpanda topic
- [ ] Spark Structured Streaming job
- [ ] Delta Lake storage (bronze / silver / gold)
- [ ] Basic analytics queries on match data

---

## Phase 4 — Analytics Dashboards

- [ ] Grafana connected to Delta Lake / PostgreSQL
- [ ] Match summary dashboard
- [ ] Player stats dashboard
- [ ] Element win rate charts

---

## Phase 5 — ML Systems

- [ ] Feature engineering from `turn_sequences`
- [ ] Win prediction model
- [ ] Card recommendation model
- [ ] MLflow experiment tracking
- [ ] Model serving endpoint in FastAPI

---

## Out of Scope (for now)

- Automatic matchmaking queue (manual room codes for Phase 1)
- Ranked ladder / ELO
- Mobile app release
- Real-time observer mode
