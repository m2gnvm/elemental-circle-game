# TODO

## Phase 2 — Architecture Hardening

### Gameplay Engine
- [ ] Extract `GameEngine` pure class (no DB imports, no HTTP)
- [ ] Move elemental multiplier logic to `GameEngine`
- [ ] Add unit tests for all 9 element matchups
- [ ] Add unit tests for turn / round progression
- [ ] Add unit tests for game-over conditions

### WebSocket
- [ ] JWT authentication on WebSocket connect (query param or first message)
- [ ] Wire `broadcast_game_state` after `play_card` in route handler
- [ ] Wire `broadcast_game_state` after `start_game`

### Database
- [ ] Migrate to `AsyncSession` (SQLAlchemy async)
- [ ] Add `GameEvent` ORM model with proper columns (not just JSON blob)
- [ ] Add `winner_id` to `Game` table
- [ ] Add indexes on `game_events.game_id`, `game_events.created_at`

### API
- [ ] Deck management endpoints (`GET/POST /decks`)
- [ ] Automatic matchmaking queue (`POST /matchmaking/join`)
- [ ] Match replay endpoint (`GET /matches/{id}/replay`)
- [ ] Structured error responses (FastAPI exception handlers)

### Testing
- [ ] pytest setup (`conftest.py`, test database, fixtures)
- [ ] Unit tests for `GameService._battle_cards`
- [ ] Unit tests for `HybridGameService`
- [ ] Integration tests for auth flow
- [ ] Integration tests for full game flow (create → join → start → play × N)
- [ ] WebSocket integration tests (`ConnectionManager`)

### Infrastructure
- [ ] GitHub Actions CI workflow (lint + test)
- [ ] `pre-commit` hooks (ruff, mypy)

---

## Phase 3 — Telemetry

- [ ] Add Redpanda to `docker-compose.yml`
- [ ] `EventService.publish(event)` → Redpanda topic
- [ ] Basic Spark Structured Streaming consumer
- [ ] Delta Lake write (bronze layer)

---

## Frontend (Flutter)
- [ ] Login screen (register + login)
- [ ] Lobby screen (create / join by room code)
- [ ] Game screen (hand display, board card, score)
- [ ] Card play action (REST call + state refresh)
- [ ] WebSocket connect for real-time push
