# Test Scripts

This folder contains test and demonstration scripts for the Elemental Circle Game.

## Scripts

### `interactive_game.py`
Interactive game where you play against an AI opponent.

**Usage:**
```bash
# Run with default 5 rounds
python test_scripts/interactive_game.py

# Run with custom number of rounds
python test_scripts/interactive_game.py --rounds 10
```

**Features:**
- You choose cards manually
- AI makes random choices
- Real-time game state display
- Coin toss to determine turn order
- Full game flow with backend integration

### `simulate_ai_fights.py`
AI vs AI simulation to test different strategies and game balance.

**Usage:**
```bash
# Run with default 10 fights, 5 rounds each
python test_scripts/simulate_ai_fights.py

# Run with custom number of fights
python test_scripts/simulate_ai_fights.py --fights 20

# Run with custom number of rounds per fight
python test_scripts/simulate_ai_fights.py --rounds 8

# Combine both options
python test_scripts/simulate_ai_fights.py --fights 15 --rounds 6
```

**Features:**
- AI vs AI battles with different strategies:
  - `random`: Random card selection
  - `highest`: Always plays highest value card
  - `lowest`: Always plays lowest value card
  - `balanced`: Plays middle value cards
- Statistical analysis of strategy performance
- Win rate calculations
- Detailed fight summaries

## Prerequisites

1. **Backend must be running:**
   ```bash
   # Start the backend server
   python -m app.main
   ```

2. **Required dependencies:**
   - `requests` (for simulate_ai_fights.py)
   - `urllib` (built-in, for interactive_game.py)

## Game Rules

- **Elements:** Fire, Water, Grass
- **Advantage:** Grass > Water > Fire > Grass
- **Scoring:** Points based on card value differences and elemental multipliers
- **Turn Order:** Alternates each round (coin toss determines who starts)

## Example Output

### Interactive Game
```
🎮 Elemental Circle Interactive Game
🌱 Grass > Water > Fire > Grass
============================================================
🎯 You vs AI - Choose your cards!
============================================================

🪙 COIN TOSS TO DETERMINE WHO GOES FIRST
==================================================
🪙 Flipping coin...
🎯 HEADS! You go first (you play the onboard card)
🤖 AI will counter-play
```

### AI Simulation
```
🎮 AI vs AI Fight Simulator
============================================================

🤖 Running 10 AI vs AI fights...
Strategies: random, highest, lowest, balanced
============================================================

🔥 FIGHT 1/10

🤖 AI Fight: RANDOM vs HIGHEST
==================================================
🎮 Game started! 5 rounds max

🔄 ROUND 1
------------------------------
🎯 AI1 goes first (onboard card)
🤖 AI2 will counter-play
🎴 AI1 plays: 3 FIRE
🎴 AI2 plays: 8 WATER
⚔️ Battle: AI2 gets 5 points
```

## Troubleshooting

- **Backend not running:** Make sure to start the backend with `python -m app.main`
- **Connection errors:** Check that the backend is running on `http://localhost:8000`
- **Import errors:** Ensure you're running from the project root directory
