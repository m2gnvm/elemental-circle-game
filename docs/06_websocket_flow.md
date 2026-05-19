# WebSocket Flow

## Endpoint

```
WS /ws/{game_id}
```

`game_id` is the integer game ID as a string (e.g. `/ws/7`).

---

## Current Behavior (Phase 1)

The server accepts connections and relays messages verbatim within a game room:

```
Client A  →  server receives text  →  broadcast to all in room (including A)
Client B  →  same
```

There is **no JSON schema enforcement** at the socket layer. Clients define their own message conventions.

**Security note:** JWT is not validated on WebSocket connect in Phase 1. Treat as development-only without edge auth.

---

## Recommended Client Message Conventions

Use typed JSON envelopes to distinguish message kinds:

```json
{ "type": "chat",         "text": "gl hf" }
{ "type": "state_refresh" }
{ "type": "player_action", "action": "played_card", "card_index": 2 }
```

---

## Planned Server Behavior (Phase 2)

After REST mutations, the server will push typed updates:

```json
{ "type": "game_state_update", "data": { ...game state... } }
{ "type": "player_action",     "player_id": 1, "data": { ... } }
```

`ConnectionManager` already defines `broadcast_game_state` and `broadcast_player_action` — they just need to be wired into game endpoints.

---

## Authoritative State Rule

The WebSocket layer **never owns game state**.

All mutations go through REST endpoints → `HybridGameService` → Redis/PostgreSQL.

WebSocket is for:
- pushing notifications after server-side mutations
- real-time chat
- low-latency status signals

---

## Flow Diagram

```
Client                      Server
  |                           |
  |-- WS connect ------------>|  ConnectionManager.connect(ws, game_id)
  |<- (accepted) -------------|
  |                           |
  |-- POST /games/{id}/play -->|  HybridGameService.play_card(...)
  |<- { points, state } ------|
  |                           |
  |  (Phase 2) server pushes  |
  |<- game_state_update -------|  broadcast_game_state(game_id, state)
  |                           |
  |-- WS disconnect ---------->|  ConnectionManager.disconnect(ws, game_id)
```

---

## Flutter Client Notes

- Use the `web_socket_channel` package — connect to `ws://host:8000/ws/<game_id>`
- Parse/stringify with `jsonDecode` / `jsonEncode` from `dart:convert`
- For production use `wss://` and ensure TLS cert is trusted
- After each `play` REST call, refresh state via `GET /games/{id}/state`

## Godot Client Notes (later phase)

- Use `WebSocketPeer` (Godot 4) — connect to `ws://host:8000/ws/<game_id>`
- Parse/stringify with `JSON.parse_string` / `JSON.stringify`
- See `docs/api-for-godot.md` for full Godot-specific reference
