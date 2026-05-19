# API reference for Godot clients

Godot talks to this backend only over **HTTPS** (REST) and **WSS** (WebSocket). Default local base URL: `http://127.0.0.1:8000`. Production should use TLS (`https://`, `wss://`).

All authenticated REST routes expect:

```http
Authorization: Bearer <access_token>
```

---

## Base paths

| Purpose | Path |
|--------|------|
| API root | `/api/v1` |
| Auth | `/api/v1/auth/...` |
| Games | `/api/v1/games/...` |
| WebSocket | `/ws/{game_id}` |
| Health | `GET /health` |

`{game_id}` in the WebSocket URL is the same integer id returned by create/join, passed as a **string** (e.g. game id `7` → path `/ws/7`).

---

## Authentication

### Register — `POST /api/v1/auth/register`

**Body (JSON)**

| Field | Type | Notes |
|-------|------|--------|
| `username` | string | |
| `email` | string | |
| `password` | string | |

**Success (200)** — example:

```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

**Errors:** `400` — `"Username already registered"` / `"Email already registered"`.

---

### Login — `POST /api/v1/auth/token`

This endpoint uses **OAuth2 password flow**: send **`application/x-www-form-urlencoded`**, not JSON.

**Body (form)**

| Field | Type | Notes |
|-------|------|--------|
| `username` | string | Same as registered username |
| `password` | string | |

**Success (200)**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors:** `401` — `"Incorrect username or password"`.

In Godot, build the body as `username=...&password=...` (URL-encoded) and set header `Content-Type: application/x-www-form-urlencoded`.

---

### Current user — `GET /api/v1/auth/me`

Requires `Authorization: Bearer ...`.

**Success (200)**

```json
{
  "id": 1,
  "username": "player1",
  "email": "a@b.com",
  "is_active": true
}
```

---

## Games

### Create — `POST /api/v1/games/create`

Requires bearer token.

**Body (JSON)** — optional; defaults apply if omitted.

| Field | Type | Default |
|-------|------|---------|
| `max_rounds` | int | `5` |

**Success (200)**

```json
{
  "game_id": 1,
  "room_code": "xYz123ab",
  "player_id": 1,
  "status": "waiting",
  "max_rounds": 5
}
```

`player_id` is the `GamePlayer` row id (used internally). `game_id` is what you use in URLs and WebSocket paths.

---

### Join — `POST /api/v1/games/join/{room_code}`

Requires bearer token. `{room_code}` is the string from create (URL-safe).

**Success (200)**

```json
{
  "game_id": 1,
  "room_code": "xYz123ab",
  "player_id": 2,
  "status": "waiting"
}
```

**Errors:** `404` — game not found; `400` — game not accepting players (e.g. not `waiting`).

---

### Start — `POST /api/v1/games/{game_id}/start`

Requires bearer token. Expects **two players** in the game (see server config `MAX_PLAYERS_PER_GAME`).

**Success (200)**

```json
{
  "game_id": 1,
  "status": "in_progress",
  "message": "Game started successfully"
}
```

**Errors:** `400` — validation / not enough players (message from server).

---

### Play card — `POST /api/v1/games/{game_id}/play?card_index={n}`

Requires bearer token. **`card_index`** is a **query parameter** (0-based index into **your** hand).

**Success (200)** — shape from `HybridGameService.play_card`:

```json
{
  "points": 8,
  "player_points": 8,
  "onboard_card": { "value": 6, "element": "grass" },
  "game_finished": false,
  "round": 2,
  "turn": 1
}
```

- `points`: points awarded **this play** (counter-player turn only; otherwise `0`).
- `onboard_card`: the card now on board after the play.
- `element` on cards is one of: `"fire"`, `"water"`, `"grass"`.

**Errors:** `404` — not a player in this game; `400` — invalid move / index / game state (`detail` string).

---

### Game state — `GET /api/v1/games/{game_id}/state`

Requires bearer token; you must be in the game.

**Success (200)**

```json
{
  "game_id": 1,
  "status": "in_progress",
  "round": 1,
  "turn": 1,
  "onboard_card": { "value": 4, "element": "water" },
  "players": [
    {
      "id": 1,
      "username": "alice",
      "points": 0,
      "cards_in_hand": 5
    },
    {
      "id": 2,
      "username": "bob",
      "points": 0,
      "cards_in_hand": 5
    }
  ],
  "your_hand": [
    { "value": 3, "element": "fire" },
    { "value": 7, "element": "grass" }
  ]
}
```

Notes:

- `players[].id` is **GamePlayer** id (matches Redis player keys).
- `your_hand` is the full hand for the authenticated user only; other players only show `cards_in_hand` count.

**Errors:** `403` — not in game; `404` — no Redis state / missing game.

---

### My games — `GET /api/v1/games/my-games`

Requires bearer token.

**Success (200)** — JSON array of:

```json
{
  "game_id": 1,
  "room_code": "xYz123ab",
  "status": "waiting",
  "players_count": 2,
  "created_at": "2026-04-18T12:00:00"
}
```

`created_at` is ISO-like timestamp string from the server.

---

## Card object (JSON)

Used in hands and as `onboard_card`:

```json
{
  "value": 6,
  "element": "fire"
}
```

- `value`: integer, typically `1`–`8` (see server `MIN_CARD_VALUE` / `MAX_CARD_VALUE`).
- `element`: `"fire"` | `"water"` | `"grass"`.

---

## WebSocket — `WS /ws/{game_id}`

### Current server behavior

1. Server **accepts** the connection and adds it to a room keyed by `game_id` (string).
2. Any **text** message received from one client is **broadcast verbatim** to all other connections in the same `game_id` room (including the sender, depending on timing).

There is **no** enforced JSON schema on the wire in `app/main.py`: payloads are opaque strings. For your own clients you can standardize JSON, for example:

```json
{ "type": "chat", "text": "gl hf" }
```

or relay copies of REST responses if you add that convention in the Godot project.

### Server-side helpers (not auto-wired to the socket loop)

`ConnectionManager` also defines JSON shapes used elsewhere in the codebase for **potential** broadcasts:

- `game_state_update` — `{ "type": "game_state_update", "data": { ... game state dict ... } }`
- `player_action` — `{ "type": "player_action", "player_id": <int>, "data": { ... } }`

The live `/ws/{game_id}` handler today only echoes `receive_text` → `broadcast_to_game`; it does **not** automatically emit these typed messages. Plan either:

- **Client-driven sync:** after each successful REST `play` or on a timer, `GET .../state` and update UI; use WebSocket only for chat or custom signals, or  
- **Server upgrade:** after mutations, call `broadcast_game_state` / `broadcast_player_action` from the game endpoints (future change).

### Security note

The WebSocket endpoint **does not validate JWT** in the current implementation. Treat open rooms as **development-only**, or put the API behind auth at the edge, or extend `websocket_endpoint` to require a token (query param or first message) before `accept()`.

---

## Godot implementation hints

- **REST:** `HTTPRequest` — set method, headers (`Authorization`, `Content-Type`), body for POST.
- **Login body:** form-urlencoded for `/auth/token`, not JSON.
- **WebSocket:** Godot 4 `WebSocketPeer` (or high-level multiplayer if you wrap it yourself); connect to `ws://host:8000/ws/<game_id>` (or `wss://` in production).
- **JSON:** Parse/stringify with `JSON.parse_string` / `JSON.stringify` on dictionaries.
- **TLS:** Use `https`/`wss` and ensure Godot trusts your CA (or use system certs).

---

## Quick flow (two players)

1. Both: `POST /auth/register` (once) → `POST /auth/token` → store `access_token`.
2. Host: `POST /games/create` → share `room_code`.
3. Guest: `POST /games/join/{room_code}`.
4. Host: `POST /games/{game_id}/start` (when two players are in lobby).
5. Both: optional `WS /ws/{game_id}` for your own messages; poll or refresh with `GET /games/{game_id}/state`.
6. On turn: `POST /games/{game_id}/play?card_index=<0-based>` with bearer token.
7. Read response + `state` to refresh UI; `status` may become `finished`.

---

## OpenAPI

Interactive schemas and “try it” UI: `GET http://<host>:8000/docs` (Swagger UI).
