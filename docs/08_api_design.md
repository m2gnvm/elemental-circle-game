# API Design

## Base URL

```
http://localhost:8000        (local)
https://your-domain.com      (production)
```

All REST routes are under `/api/v1`.

---

## Authentication

JWT Bearer tokens. All authenticated endpoints require:

```http
Authorization: Bearer <access_token>
```

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register new user |
| POST | `/api/v1/auth/token` | — | Login (OAuth2 password flow, form-encoded) |
| GET | `/api/v1/auth/me` | ✓ | Current user info |

**Login note:** Send `application/x-www-form-urlencoded`, not JSON.

---

## Games

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/games/create` | ✓ | Create game room |
| POST | `/api/v1/games/join/{room_code}` | ✓ | Join by room code |
| POST | `/api/v1/games/{game_id}/start` | ✓ | Start game (host) |
| POST | `/api/v1/games/{game_id}/play` | ✓ | Play a card (`?card_index=N`) |
| GET | `/api/v1/games/{game_id}/state` | ✓ | Get current game state |
| GET | `/api/v1/games/my-games` | ✓ | List my games |

---

## WebSocket

```
WS /ws/{game_id}
```

Room-scoped text relay. See `docs/06_websocket_flow.md` for full details.

---

## Utility

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI (OpenAPI) |

---

## Response Conventions

- Success: `200 OK` with JSON body
- Validation error: `400 Bad Request` with `{ "detail": "..." }`
- Auth failure: `401 Unauthorized`
- Forbidden: `403 Forbidden`
- Not found: `404 Not Found`

---

## Future Endpoints (Phase 2+)

```
GET  /api/v1/matches/{id}/replay     # Event log for replay
GET  /api/v1/users/{id}/stats        # Win/loss stats
POST /api/v1/matchmaking/join        # Automatic matchmaking queue
GET  /api/v1/decks                   # Deck management
POST /api/v1/decks
```

---

## OpenAPI / Swagger

Interactive docs available at `GET http://localhost:8000/docs` while the server is running.
