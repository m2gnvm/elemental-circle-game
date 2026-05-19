"""
Pure game engine — no DB, no HTTP, no Redis, no side effects.

All functions are deterministic given the same inputs (except the random
helpers, which are isolated so tests can control randomness via seeding).
"""
from __future__ import annotations

import random
from typing import Any

ELEMENTS: tuple[str, ...] = ("fire", "water", "grass")

# (played_element, onboard_element) → advantage multiplier
# Fire beats Grass, Grass beats Water, Water beats Fire
_ADVANTAGE: dict[tuple[str, str], float] = {
    ("fire", "grass"): 2.0,
    ("grass", "water"): 2.0,
    ("water", "fire"): 2.0,
}


class GameEngine:
    """
    Stateless game logic. All methods are static — instantiation is optional.

    Card shape: {"value": int, "element": str}
    """

    # ------------------------------------------------------------------
    # Elemental system
    # ------------------------------------------------------------------

    @staticmethod
    def elemental_multiplier(onboard_element: str, played_element: str) -> float:
        """
        Return the multiplier applied to the played card's value.

        2.0 — played element beats onboard element
        1.0 — same element
        0.5 — played element loses to onboard element
        """
        if played_element == onboard_element:
            return 1.0
        return _ADVANTAGE.get((played_element, onboard_element), 0.5)

    @staticmethod
    def resolve_battle(
        onboard_card: dict[str, Any],
        played_card: dict[str, Any],
    ) -> float:
        """
        Calculate points for the counter-player (turn 2).

        Formula: (played_value × multiplier) − onboard_value

        Points can be negative (played card is weaker than the board card).
        Turn 1 (board-setter) always scores 0 — enforce that in the caller.
        """
        multiplier = GameEngine.elemental_multiplier(
            onboard_card["element"], played_card["element"]
        )
        return played_card["value"] * multiplier - onboard_card["value"]

    # ------------------------------------------------------------------
    # Turn / round progression
    # ------------------------------------------------------------------

    @staticmethod
    def next_turn_state(
        current_turn: int,
        current_round: int,
        max_rounds: int,
    ) -> dict[str, Any]:
        """
        Return the next turn/round values after a card has been played.

        Returns a dict: {"turn": int, "round": int, "round_complete": bool, "game_over": bool}
        """
        if current_turn == 1:
            return {
                "turn": 2,
                "round": current_round,
                "round_complete": False,
                "game_over": False,
            }

        # Turn 2 just finished → round is complete
        next_round = current_round + 1
        game_over = next_round > max_rounds
        return {
            "turn": 1,
            "round": next_round,
            "round_complete": True,
            "game_over": game_over,
        }

    @staticmethod
    def is_game_over(
        round_number: int,
        max_rounds: int,
        hands: list[list[Any]],
    ) -> bool:
        """
        True when the game should end.

        Ends if: all rounds are exhausted, or any player has an empty hand.
        """
        if round_number > max_rounds:
            return True
        return any(len(hand) == 0 for hand in hands)

    @staticmethod
    def determine_winner(player_points: dict[int, float]) -> int | None:
        """
        Return the player_id with the highest points.
        Returns None on a draw (equal highest points).
        """
        if not player_points:
            return None
        max_points = max(player_points.values())
        leaders = [pid for pid, pts in player_points.items() if pts == max_points]
        return leaders[0] if len(leaders) == 1 else None

    # ------------------------------------------------------------------
    # Card creation (random helpers — isolate randomness here)
    # ------------------------------------------------------------------

    @staticmethod
    def random_card(min_value: int = 1, max_value: int = 8) -> dict[str, Any]:
        """Create a single random card."""
        return {
            "value": random.randint(min_value, max_value),
            "element": random.choice(list(ELEMENTS)),
        }

    @staticmethod
    def deal_hand(
        size: int,
        min_value: int = 1,
        max_value: int = 8,
    ) -> list[dict[str, Any]]:
        """Deal a hand of `size` random cards."""
        return [GameEngine.random_card(min_value, max_value) for _ in range(size)]
