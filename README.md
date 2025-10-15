# Elemental Circle Game Backend

A strategic card game with elemental combat system built with FastAPI, PostgreSQL, and Redis using a hybrid architecture for optimal performance.

## Features

- **Real-time Multiplayer**: WebSocket support for live gameplay
- **Hybrid Architecture**: Redis for fast game state + PostgreSQL for persistent data
- **Authentication**: JWT-based user authentication
- **Game Rooms**: Create and join game rooms with unique codes
- **Elemental Combat**: Rock-paper-scissors style elemental system
- **Dynamic Card Generation**: No database dependency for cards
- **Event Analytics**: Comprehensive game event logging
- **Scalable Architecture**: Ready for production deployment

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Flutter (Web, Mobile, Desktop)
- **Database**: PostgreSQL with SQLAlchemy ORM (persistent data & analytics)
- **Caching**: Redis for real-time game state management
- **Authentication**: JWT tokens
- **Real-time**: WebSocket connections

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
   python interactive_game.py --rounds 5
   
   # AI vs AI simulation
   python simulate_ai_fights.py --fights 10 --rounds 3
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

### Phase 2: Web Application
- **Flutter Web App**: Full-featured web application with modern UI
- **Social Features**: Friends list, chat, and social interactions
- **Enhanced UI/UX**: Beautiful game interface with animations
- **Progressive Web App**: Installable web app with offline capabilities

### Phase 3: Production Scale
- **Cloud Deployment**: AWS/Azure production deployment
- **Load Balancing**: Handle thousands of concurrent players
- **Advanced Analytics**: ML-powered game balancing and cheat detection
- **Monetization**: Premium features and cosmetic items

### Phase 4: Platform Expansion (Optional)
- **Mobile Apps**: Native iOS and Android applications
- **Steam Integration**: Desktop version for Steam platform
- **Cross-Platform**: Full cross-platform multiplayer support

## Technical Specifications

### Current Architecture
- **Hybrid Database**: Redis (game state) + PostgreSQL (persistent data)
- **Real-time Communication**: WebSocket with Redis pub/sub
- **Containerization**: Docker with multi-service orchestration
- **Authentication**: JWT-based secure authentication

