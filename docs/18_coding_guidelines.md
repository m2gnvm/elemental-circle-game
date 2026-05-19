# Coding Guidelines

## Python / Backend

### Type Hints

Use type hints on all function signatures:

```python
# ✅
def play_card(self, game_id: int, player_id: int, card_index: int) -> dict[str, Any]:

# ❌
def play_card(self, game_id, player_id, card_index):
```

### Async First

Use `async def` everywhere I/O is involved:

```python
# ✅
async def get_game_state(game_id: int, db: AsyncSession) -> GameStateResponse:

# ❌ (in a route handler)
def get_game_state(game_id: int, db: Session) -> GameStateResponse:
```

### Thin Routes

Routes call services and return. No business logic in route handlers:

```python
# ✅
@router.post("/games/{game_id}/play")
async def play_card(game_id: int, card_index: int, ...):
    result = await game_service.play_card(game_id, player.id, card_index)
    return result

# ❌
@router.post("/games/{game_id}/play")
async def play_card(game_id: int, ...):
    game = db.query(Game).filter(...).first()
    if game.status != "in_progress":
        raise ...
    # 50 more lines of logic
```

### Service Layer Pattern

Separate `routes → services → repositories`:
- Routes: parse input, call service, return output
- Services: business logic, validation, orchestration
- Repositories / ORM: data access only

### Small Functions

Each function should do one thing. Extract helpers rather than growing functions:

```python
# ✅ — clear intent, testable in isolation
def _get_elemental_multiplier(self, onboard: str, played: str) -> float:
    ...

def _battle_cards(self, onboard_card: dict, played_card: dict) -> float:
    multiplier = self._get_elemental_multiplier(...)
    ...
```

---

## Gameplay Logic

### Determinism Rule

Gameplay logic must be deterministic given the same inputs:
- No random calls inside `play_card` resolution (randomness only at deal time)
- No side effects (no DB writes inside pure calculation functions)
- No WebSocket calls inside game engine

### Isolation Rule

`GameEngine` / `GameService` must not import from:
- `app.websocket`
- `fastapi`
- HTTP-related modules

---

## General

- Prefer readability over cleverness
- Avoid premature optimization
- Keep modules small and focused
- Use `Pydantic` models for request/response validation (not raw dicts in routes)
- No magic numbers — use `settings.*` constants
