# Data Engineering

## Goals

- Capture telemetry from every match
- Build analytics pipelines
- Create replay archives
- Generate ML training datasets

---

## Phase 1 Foundation (Now)

`game_events` table in PostgreSQL captures every meaningful game action.
This is the raw data source for all future pipelines.

Key fields: `event_type`, `game_id`, `player_id`, `turn`, `round`, `payload`, `created_at`.

---

## Phase 3 — Streaming Pipeline

```
game_events (PostgreSQL)
        ↓  CDC or batch export
Redpanda topic: game-events
        ↓
Spark Streaming (Structured Streaming)
        ↓
Delta Lake
  ├── bronze/  (raw events)
  ├── silver/  (cleaned, typed)
  └── gold/    (aggregated metrics)
        ↓
Analytics queries / dashboards
```

### Redpanda

Kafka-compatible, runs in Docker.
Receives events either via:
- Change Data Capture (CDC) from Postgres
- Direct publish from `EventService` (simpler for Phase 3)

### Spark / Databricks

- Databricks for managed Spark
- Delta Lake for ACID transactions on the data lake
- PySpark for transformations

---

## Planned Datasets

| Dataset | Description |
|---------|-------------|
| `match_summaries` | One row per match: winner, duration, round count |
| `card_play_stats` | Element win rates, average effective values |
| `player_stats` | Win rate, avg score, preferred elements per player |
| `turn_sequences` | Full ordered event sequence per match (for replay / ML) |

---

## ML Use Cases (Phase 5)

- Predict match winner from partial game state
- Recommend card to play given hand + board
- Detect anomalous player behaviour
- Balance analysis: element win rate distribution

MLflow will track experiments and model versions.

---

## Principles

- `game_events` must never be deleted or mutated — append-only
- Raw (bronze) data is always preserved
- All transformations are reproducible from raw events
