# Elemental Circle Game

A strategic card game with an elemental combat system. The **game client** is built in **Godot** (mobile-first; desktop and optional web export). The **backend** is **FastAPI** with **WebSockets**, **Redis** for live state, and **PostgreSQL** for persistence, analytics, and data/ML workflows.

## Features

- **Real-time Multiplayer**: WebSocket support for live gameplay
- **Hybrid Architecture**: Redis for fast game state + PostgreSQL for persistent data
- **Authentication**: JWT-based user authentication
- **Game Rooms**: Create and join game rooms with unique codes
- **Elemental Combat**: Rock-paper-scissors style elemental system
- **Dynamic Card Generation**: No database dependency for cards
- **Event Analytics**: Comprehensive game event logging (foundation for ML and product analytics)
- **Scalable Architecture**: Ready for production deployment

## Tech Stack

| Layer | Technology |
|--------|------------|
| **Game client** | Godot 4+ (GDScript or C#) — HTTP + WebSocket to the API |
| **Backend** | FastAPI + Python |
| **Real-time state** | Redis (rooms, hands, turns, TTL) |
| **Persistent data** | PostgreSQL + SQLAlchemy (users, events, stats) |
| **Real-time transport** | WebSocket (`/ws/{game_id}`) + REST (`/api/v1/...`) |
| **Auth** | JWT |
| **Data / ML** | Event stream in PostgreSQL → batch or streaming jobs, feature stores, model training/serving (see Architecture) |

## System Architecture

```
+------------------------------------------------------------------+
|  Godot client (Android / iOS / desktop; web export optional)      |
|  REST: auth, rooms, play, state |  WebSocket: live game sync      |
+----------------------------+-------------------------------------+
                             | HTTPS / WSS (JWT)
+----------------------------v-------------------------------------+
|  FastAPI                                                        |
|  HTTP API | WebSocket hub | Auth | Game / hybrid services       |
+----------------------------+-------------------------------------+
               |                               |
               v                               v
+---------------------------+    +----------------------------------+
|  Redis                    |    |  PostgreSQL                      |
|  Live game state, cache   |    |  Users, game events, analytics   |
+---------------------------+    +----------------+-----------------+
                                               |
                                               v
                              +----------------+----------------------+
                              |  Data / ML (Python ecosystem)       |
                              |  ETL, dashboards, experiments,      |
                              |  balance / cheat / engagement models|
                              +-------------------------------------+
```

- **Godot** never talks to Redis or Postgres directly; it only uses the **public API** (REST + WebSocket). That keeps one contract and lets you change storage without shipping a new client.
- **PostgreSQL** (especially **game events** and aggregates) is the natural **source of truth for analytics and ML**: export to a warehouse, train offline, or serve batch/online predictions from FastAPI or a sidecar service when you add those endpoints.

## Quick Start

### Option 1: Docker Deployment (Recommended)

**Prerequisites:**
- Docker Desktop installed and running
- WSL 2 integration enabled

**Deploy with one command:**
```bash
./deploy_local.sh
```

**Check health:**
```bash
./check_docker_health.sh
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Database**
   ```bash
   # Install PostgreSQL and Redis
   # Update DATABASE_URL and REDIS_URL in local.env
   # The hybrid architecture uses both databases:
   # - PostgreSQL: User accounts, game events, analytics
   # - Redis: Real-time game state, player hands, points
   ```

3. **Run the Server**
   ```bash
   python -m app.main
   ```

4. **Test the Game**
   ```bash
   # Interactive game (you vs AI)
   python test_scripts/interactive_game.py --rounds 5
   
   # AI vs AI simulation
   python test_scripts/simulate_ai_fights.py --fights 10 --rounds 3
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Games
- `POST /api/v1/games/create` - Create new game room
- `POST /api/v1/games/join/{room_code}` - Join game by room code
- `POST /api/v1/games/{game_id}/start` - Start the game
- `POST /api/v1/games/{game_id}/play` - Play a card
- `GET /api/v1/games/{game_id}/state` - Get game state
- `GET /api/v1/games/my-games` - Get user's games

### WebSocket
- `WS /ws/{game_id}` - Real-time game updates

**Client integration (Godot):** request/response shapes, WebSocket behavior, and security notes are in [docs/api-for-godot.md](docs/api-for-godot.md).

## Architecture

### Hybrid Database Design
- **Redis**: Fast game state storage (sub-millisecond access)
  - Player hands, points, game status
  - Real-time turn management
  - Automatic cleanup with TTL
- **PostgreSQL**: Persistent data & analytics
  - User accounts and authentication
  - Game events and statistics
  - Player performance analytics

### Key Components
- **HybridGameService**: Combines Redis + PostgreSQL operations
- **RedisGameService**: Manages fast game state
- **EventService**: Logs events for analytics
- **Dynamic Card Generation**: No database dependency

### Data / ML Engineering (roadmap)
- **Ingestion**: Existing event logging → structured tables or exports (CSV/Parquet, warehouse sync).
- **Offline**: Notebooks or pipelines (e.g. pandas, Polars, scikit-learn, PyTorch) for balance analysis, segmentation, churn, or bot policy research.
- **Online**: Optional FastAPI routes or workers that read precomputed scores or call a model; keep **gameplay-critical paths** fast and Redis-friendly.
- **MLOps**: Version models, track experiments, and separate **training** from **serving** as traffic grows.

## Game Rules

### Core Mechanics
1. **Elements**: Fire, Water, Grass
2. **Elemental Advantages**: 
   - Grass beats Water (2x multiplier) / Water loses to Grass (0.5x multiplier)
   - Water beats Fire (2x multiplier) / Fire loses to Water (0.5x multiplier)
   - Fire beats Grass (2x multiplier) / Grass loses to Fire (0.5x multiplier)
   - Same elements = 1x multiplier (no advantage)
3. **Card Values**: 1-8 points per card
4. **Turn System**: 
   - Player 1 plays onboard card
   - Player 2 counter-plays
   - Points awarded to counter-player only
5. **Scoring Formula**: 
   - `Points = (played_card_value × elemental_multiplier) - onboard_card_value`
   - Example: Play 6 Grass vs 4 Water = (6 × 2) - 4 = 8 points
6. **Winning**: Player with most total points after all rounds

## Future Upgrades

### Phase 1: Enhanced Gameplay
- **AI Opponents**: Smart AI with different difficulty levels and strategies
- **Tournament Mode**: Multi-round tournaments with bracket system
- **Custom Game Modes**: Different rule sets and card variations
- **Player Statistics**: Detailed performance tracking and leaderboards

### Phase 2: Godot Client & Social
- **Godot app**: Mobile-first builds (Android/iOS), desktop; optional HTML5 export for demos
- **Social Features**: Friends list, chat, and social interactions
- **Polish**: Card motion, VFX, and responsive layouts for many screen sizes

### Phase 3: Production Scale & Intelligence
- **Cloud Deployment**: AWS/Azure production deployment
- **Load Balancing**: Handle thousands of concurrent players
- **Data & ML**: Deeper pipelines on PostgreSQL events — balance patches, anomaly/cheat signals, engagement models
- **Monetization**: Premium features and cosmetic items

### Phase 4: Platform Expansion (Optional)
- **Steam / desktop stores**: Packaged Godot desktop builds
- **Cross-Platform**: Same backend; clients share the API contract

## Technical Specifications

### Current Architecture
- **Hybrid Database**: Redis (game state) + PostgreSQL (persistent data)
- **Real-time Communication**: WebSocket with Redis pub/sub
- **Containerization**: Docker with multi-service orchestration
- **Authentication**: JWT-based secure authentication
- **Client**: Godot — HTTP for REST, WebSocket for live sync; no direct DB access
