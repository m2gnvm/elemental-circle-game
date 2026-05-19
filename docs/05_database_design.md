# Database Design

## PostgreSQL Tables

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | |
| username | string | unique |
| email | string | unique |
| password_hash | string | bcrypt |
| is_active | boolean | default true |

### `games`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | |
| room_code | string | unique, URL-safe |
| status | enum | `waiting` / `in_progress` / `finished` |
| max_rounds | integer | default 5 |
| round_number | integer | current round |
| current_turn | integer | 1 or 2 |
| game_state | JSON | snapshot blob |

### `game_players`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | (used as `player_id` in API) |
| game_id | FK → games | |
| user_id | FK → users | |
| player_number | integer | 1 or 2 |
| points | integer | accumulated score |
| hand | JSON | array of card dicts |

### `game_cards`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | |
| game_id | FK → games | |
| card_value | integer | |
| card_element | string | `fire`/`water`/`grass` |
| position | string | `onboard` (current board card) |

### `game_events`
| Column | Type | Notes |
|--------|------|-------|
| id | integer PK | |
| game_id | FK → games | |
| event_type | string | e.g. `CARD_PLAYED` |
| player_id | integer | nullable |
| turn | integer | |
| round | integer | |
| payload | JSON | event-specific data |
| created_at | datetime | |

---

## Redis Keys

| Key pattern | Value | Purpose |
|-------------|-------|---------|
| `game:{game_id}:state` | JSON | Live game state during match |
| `game:{game_id}:player:{player_id}:hand` | JSON list | Player hand (fast access) |
| `matchmaking:queue` | list | Waiting player IDs |

Redis data is the source of truth **during** an active match.
PostgreSQL receives the final record after match completion.

---

## Notes

- `hand` on `game_players` is a JSON column (list of `{value, element}` dicts) — simple for Phase 1.
- Phase 2 should consider migrating hands to proper `cards` + `player_cards` join table for query flexibility.
- `game_events` is the foundation for the replay system and analytics pipeline.
