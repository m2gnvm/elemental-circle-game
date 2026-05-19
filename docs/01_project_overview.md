# Elemental Circle

## Overview

Elemental Circle is an online multiplayer turn-based card game focused on elemental counter-play mechanics.

The project serves two goals:
1. Build a playable online game
2. Learn scalable backend and data engineering systems

---

## Core Gameplay

### Elements
- Fire
- Water
- Grass

### Mechanics
- Turn-based combat
- Elemental advantages (Fire > Grass > Water > Fire)
- Card power values (1–8)
- Best-of-N rounds per match

---

## Main Technical Goals

- FastAPI backend
- Flutter frontend (initial), Godot (later)
- WebSocket multiplayer
- Event-driven architecture
- Replay system
- Streaming telemetry
- Databricks learning
- AWS learning

---

## Tech Stack

### Frontend
- Flutter (initial)
- Godot 4 (later phase)

### Backend
- Python 3.11+
- FastAPI
- WebSockets (via FastAPI)

### Databases
- PostgreSQL (persistent state)
- Redis (live game state, sessions, queues)

### Infrastructure
- Docker
- Docker Compose
- Nginx

### Future Stack
- Apache Spark
- Databricks / Delta Lake
- Redpanda (event streaming)
- MLflow

---

## Current Status

Phase 1 backend is functional:
- JWT authentication
- Game create / join / start / play via REST
- WebSocket room broadcast (opaque text relay)
- Redis-backed live game state (`HybridGameService`)
- PostgreSQL persistence for users, games, events

See `docs/api-for-godot.md` for the full REST + WebSocket reference.
