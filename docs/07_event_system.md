# Event System

## Philosophy

Every meaningful game action produces a structured, immutable event stored in `game_events`.
Events are the ground truth for replays, analytics, debugging, and future ML datasets.

---

## Event Types

| Event | When |
|-------|------|
| `MATCH_CREATED` | Game room is created |
| `PLAYER_JOINED` | A player joins the room |
| `MATCH_STARTED` | Host starts the game |
| `TURN_STARTED` | A new turn begins |
| `CARD_PLAYED` | A player plays a card |
| `DAMAGE_APPLIED` | Points awarded after counter play |
| `ROUND_FINISHED` | Both players have played in a round |
| `MATCH_FINISHED` | Game reaches terminal state |

---

## Event Schema

```json
{
  "event_type": "CARD_PLAYED",
  "game_id": 1,
  "player_id": 2,
  "turn": 1,
  "round": 3,
  "payload": {
    "card": { "value": 6, "element": "grass" },
    "onboard_card": { "value": 4, "element": "water" },
    "effective_value": 12,
    "points_awarded": 8
  },
  "created_at": "2026-05-06T20:00:00Z"
}
```

---

## Storage

Events are persisted to `game_events` (PostgreSQL) via `EventService`.
Redis does **not** store events — only mutable live state.

---

## Replay System (Phase 2)

By replaying the ordered event log for a `game_id`, any match can be reconstructed deterministically:

```
MATCH_CREATED → PLAYER_JOINED × 2 → MATCH_STARTED
→ [TURN_STARTED → CARD_PLAYED → DAMAGE_APPLIED → ROUND_FINISHED] × N
→ MATCH_FINISHED
```

This requires:
- `EventService.get_events(game_id)` ordered by `created_at`
- A pure `GameEngine.apply(event)` function (no side effects, no DB calls)

---

## Analytics Pipeline (Phase 3)

```
game_events (PostgreSQL)
        ↓
Redpanda topic: game-events
        ↓
Spark Streaming job
        ↓
Delta Lake (bronze / silver / gold layers)
        ↓
Analytics queries / MLflow datasets
```

---

## Coding Guideline

- `EventService` is the only place that writes to `game_events`
- Services call `EventService.record(event_type, game_id, payload, ...)` — never write directly to the table
- Keep `payload` JSON-serialisable (no Python objects)
