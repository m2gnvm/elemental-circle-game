# Architecture

## Architecture Style

The project starts as:
- **Modular Monolith** — all modules in one deployable unit
- **Async-first** — `async/await` throughout FastAPI, DB, and WebSocket layers
- **Event-driven internally** — gameplay actions emit structured events

Microservices are intentionally avoided in early phases.

---

## High-Level Structure

```
Frontend (Flutter → Godot later)
          ↓  REST (HTTPS)  /  WebSocket (WSS)
FastAPI Backend  ←→  Redis (live state)
          ↓
     PostgreSQL (persistence)
```

---

## Main Principles

### Authoritative Server

The backend owns:
- game state validation
- card battle resolution
- point calculation
- match lifecycle (waiting → in_progress → finished)

Clients only:
- send actions (play card, join game)
- render the state returned by the server

### Event-Driven Design

Every meaningful game action creates a structured event stored in `match_events`:

```
CardPlayed → DamageCalculated → TurnEnded → RoundFinished → MatchFinished
```

Benefits:
- replay system
- analytics pipelines
- debugging
- ML training datasets

### Hybrid State Strategy

- **Redis** holds the live, mutable game state during a match (fast reads/writes)
- **PostgreSQL** stores the final record and event log after the match

`HybridGameService` coordinates between both stores.

---

## Module Layout

```
app/
├── api/v1/        # Route handlers (thin — delegate to services)
├── core/          # Config, DB engine
├── models/        # SQLAlchemy ORM models
├── services/      # Business logic (game, auth, events, redis)
└── websocket/     # ConnectionManager (room broadcast)
```

---

## Future Architecture

```
Game Backend
      ↓
Redpanda (event streaming)
      ↓
Spark Streaming
      ↓
Delta Lake
      ↓
Analytics / MLflow
```
