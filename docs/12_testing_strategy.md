# Testing Strategy

## Priorities

1. **Gameplay logic** — must be deterministic and unit-tested
2. **API integration** — endpoints + auth + DB
3. **WebSocket** — multiplayer sync

---

## Test Types

### Unit Tests — Gameplay Logic

Test `GameService` and `HybridGameService` in isolation from the DB and HTTP layer.

Focus areas:
- `_battle_cards()` — elemental multiplier calculation
- `_get_elemental_multiplier()` — all 9 element combinations
- Turn / round progression logic
- Game-over conditions

```python
def test_fire_beats_grass():
    service = GameService(db=None)  # no DB needed for pure logic
    result = service._get_elemental_multiplier("grass", "fire")
    assert result == 2.0

def test_water_loses_to_grass():
    service = GameService(db=None)
    result = service._get_elemental_multiplier("grass", "water")
    assert result == 0.5
```

### Integration Tests — API + DB

Use `pytest` + `httpx.AsyncClient` + SQLite in-memory (or test Postgres via Docker):

```python
async def test_register_and_login(client):
    await client.post("/api/v1/auth/register", json={...})
    resp = await client.post("/api/v1/auth/token", data={...})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
```

### WebSocket Tests

Test `ConnectionManager` room broadcast in isolation:

```python
async def test_broadcast_to_game():
    manager = ConnectionManager()
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    await manager.connect(ws1, "game-1")
    await manager.connect(ws2, "game-1")
    await manager.broadcast_to_game("game-1", "hello")
    assert ws1.received == ["hello"]
    assert ws2.received == ["hello"]
```

---

## Test Tooling

| Tool | Purpose |
|------|---------|
| `pytest` | Test runner |
| `pytest-asyncio` | Async test support |
| `httpx` | Async HTTP client for integration tests |
| `fakeredis` | In-memory Redis mock |

---

## Existing Test Scripts

`test_scripts/` contains manual / simulation scripts (not pytest):

- `interactive_game.py` — manual two-player session
- `simulate_ai_fights.py` — automated AI vs AI runs

These are for smoke testing and exploration, not CI.

---

## Phase 2 Goals

- Full pytest suite with >80% coverage on `services/`
- CI pipeline running tests on every PR
- Deterministic game engine extracted and fully unit-tested
