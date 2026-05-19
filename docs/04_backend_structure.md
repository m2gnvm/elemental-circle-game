# Backend Structure

## Directory Layout

```
app/
├── api/
│   └── v1/
│       ├── api.py          # Aggregates all sub-routers
│       ├── auth.py         # /auth/* endpoints
│       └── games.py        # /games/* endpoints
├── core/
│   ├── config.py           # Settings (Pydantic BaseSettings)
│   └── database.py         # SQLAlchemy engine + session factory
├── models/
│   ├── card.py             # Card, ElementType
│   ├── game.py             # Game, GamePlayer, GameCard
│   ├── user.py             # User
│   └── events.py           # GameEvent
├── services/
│   ├── auth_service.py     # JWT, password hashing, user lookup
│   ├── game_service.py     # Core game logic (DB-only)
│   ├── hybrid_game_service.py  # Redis + DB coordination
│   ├── event_service.py    # Event persistence
│   └── redis_service.py    # Redis helpers
├── websocket/
│   └── connection_manager.py   # Room-based broadcast
└── main.py                 # FastAPI app, lifespan, WebSocket endpoint
```

---

## Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| `api/v1/` | HTTP routing, request parsing, auth dependencies — keep thin |
| `services/` | All business logic, validation, state mutation |
| `models/` | ORM schema only — no business logic |
| `core/` | Config, DB session — infrastructure only |
| `websocket/` | Connection lifecycle and broadcast — no game logic |

---

## Key Principles

### Thin Routes

Routes should only:
1. Parse and validate request input
2. Call a service method
3. Return the result

No game logic in routes.

### Service Isolation

`game_service.py` must not import from `websocket/` or depend on HTTP concerns.
Gameplay logic is deterministic and testable in isolation.

### Async First

Use `async def` for:
- all route handlers
- WebSocket handlers
- Redis operations
- anywhere I/O is involved

SQLAlchemy sessions are currently sync (`Session`) — migrate to `AsyncSession` in Phase 2.

---

## Config Reference (`core/config.py`)

Key settings (set via environment / `.env`):

| Setting | Default | Purpose |
|---------|---------|---------|
| `MAX_PLAYERS_PER_GAME` | 2 | Players per match |
| `CARDS_PER_PLAYER` | 5 | Starting hand size |
| `MIN_CARD_VALUE` | 1 | Lowest card value |
| `MAX_CARD_VALUE` | 8 | Highest card value |
| `SECRET_KEY` | — | JWT signing key |
| `DATABASE_URL` | — | PostgreSQL DSN |
| `REDIS_URL` | — | Redis DSN |
