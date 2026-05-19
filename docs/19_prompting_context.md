# Prompting Context

This file gives AI coding assistants (Cursor, Codex, Claude Code, Copilot, ChatGPT) fast context for this project.

---

## Project Identity

- **Name:** Elemental Circle
- **Type:** Online multiplayer turn-based card game
- **Backend:** Python 3.11 + FastAPI + WebSockets
- **Frontend:** Flutter (initial), Godot 4 (later phase)
- **Databases:** PostgreSQL (persistence) + Redis (live state)
- **Infrastructure:** Docker Compose + Nginx

---

## Architecture in One Paragraph

Modular monolith, async-first FastAPI backend. Game state lives in Redis during a match; PostgreSQL stores users, games, and an append-only event log (`game_events`). `HybridGameService` coordinates both. WebSocket layer (`ConnectionManager`) is a dumb room broadcaster — game logic lives in services only. The backend is always authoritative; clients send actions and render state.

---

## Elemental System

```
Fire  → beats → Grass  (×2.0 multiplier)
Grass → beats → Water  (×2.0 multiplier)
Water → beats → Fire   (×2.0 multiplier)
Losing element: ×0.5 multiplier
Same element:   ×1.0 multiplier
```

Points = `(played_card.value × multiplier) − onboard_card.value`
Only the counter player (turn 2) scores points.

---

## Current Phase

Phase 1 is complete. Working on Phase 2:
- Extract pure `GameEngine` class
- WebSocket push after mutations
- Async SQLAlchemy migration
- pytest suite

---

## Code Generation Rules

When generating code for this project:

1. Use `async def` for all I/O-touching functions
2. Add type hints on all function signatures
3. Keep route handlers thin — delegate to services
4. Keep gameplay logic isolated from WebSocket and HTTP layers
5. Use `settings.*` for constants (never hardcode game config values)
6. Use Pydantic response models, not raw dicts in route return values
7. Log errors with context; don't swallow exceptions
8. Prefer explicit over implicit

---

## File Map

| What you want | Where |
|---------------|-------|
| FastAPI app entry point | `app/main.py` |
| API routes | `app/api/v1/` |
| Game logic | `app/services/game_service.py`, `app/services/hybrid_game_service.py` |
| Redis helpers | `app/services/redis_service.py` |
| Event recording | `app/services/event_service.py` |
| WebSocket rooms | `app/websocket/connection_manager.py` |
| ORM models | `app/models/` |
| Config / settings | `app/core/config.py` |
| REST API reference | `docs/api-for-godot.md` |

---

## Do Not

- Do not put game logic in route handlers
- Do not import `websocket` modules from `services/`
- Do not use synchronous `requests` library in async code
- Do not hardcode player counts, card values, or round limits — use `settings`
