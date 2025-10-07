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
- **Database**: PostgreSQL with SQLAlchemy ORM (persistent data & analytics)
- **Caching**: Redis for real-time game state management
- **Authentication**: JWT tokens
- **Real-time**: WebSocket connections
- **API Documentation**: Auto-generated OpenAPI/Swagger

## Quick Start

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

1. **Elements**: Fire, Water, Grass
2. **Advantages**: Grass > Water > Fire > Grass
3. **Card Values**: 1-8 points
4. **Scoring**: Points = (played_value × elemental_multiplier) - onboard_value
5. **Winning**: Player with most points when all cards are played

## Development

This project is designed to showcase skills for:
- **Game Infrastructure Developer** roles
- **ML Ops Engineer** positions

Key architectural decisions demonstrate:
- **Hybrid Database Architecture**: Redis + PostgreSQL for optimal performance
- **High-performance async systems**: Sub-millisecond game state access
- **Real-time multiplayer capabilities**: WebSocket + Redis pub/sub
- **Scalable microservices architecture**: Container-ready with Docker
- **Production-ready deployment patterns**: Kubernetes, monitoring, CI/CD
- **Event-driven analytics**: Comprehensive game event logging

