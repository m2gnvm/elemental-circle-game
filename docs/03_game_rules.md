# Game Rules

## Elements

Three elements form a cyclic advantage:

```
Fire  → beats →  Grass
Grass → beats →  Water
Water → beats →  Fire
```

---

## Match Structure

- Configurable number of rounds (`max_rounds`, default 5)
- Each round has 2 turns (one per player)
- Turn 1: first player places a card on the board
- Turn 2: second player plays a counter card and scores points

---

## Elemental Advantage

Applied as a multiplier to the played card's value before comparing:

| Situation | Multiplier |
|-----------|-----------|
| Played element beats board element | ×2.0 |
| Same element | ×1.0 |
| Played element loses to board element | ×0.5 |

### Point Calculation

```
effective_value = played_card.value × elemental_multiplier
points_this_turn = effective_value − onboard_card.value
```

Only the **counter player** (turn 2) receives points. Turn 1 establishes the board card.

---

## Card Object

```json
{
  "value": 6,
  "element": "fire"
}
```

- `value`: integer 1–8 (configurable via `MIN_CARD_VALUE` / `MAX_CARD_VALUE`)
- `element`: `"fire"` | `"water"` | `"grass"`

---

## Example Round

1. Player A plays `{ value: 4, element: "water" }` → board card set.
2. Player B plays `{ value: 6, element: "grass" }` → Grass beats Water (×2.0).
   - `effective = 6 × 2 = 12`
   - `points = 12 − 4 = 8`
   - Player B scores 8 points this turn.

---

## Game End

The game ends when:
- All rounds are completed (`round_number > max_rounds`), or
- Any player runs out of cards
