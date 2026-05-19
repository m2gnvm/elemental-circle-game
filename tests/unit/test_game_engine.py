"""Unit tests for GameEngine — pure logic, no DB, no HTTP, no Redis."""
import random
import pytest

from app.engine.game_engine import GameEngine, ELEMENTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def card(value: int, element: str) -> dict:
    return {"value": value, "element": element}


# ---------------------------------------------------------------------------
# elemental_multiplier — all 9 combinations
# ---------------------------------------------------------------------------

class TestElementalMultiplier:
    # Advantages (×2.0)
    def test_fire_beats_grass(self):
        assert GameEngine.elemental_multiplier("grass", "fire") == 2.0

    def test_grass_beats_water(self):
        assert GameEngine.elemental_multiplier("water", "grass") == 2.0

    def test_water_beats_fire(self):
        assert GameEngine.elemental_multiplier("fire", "water") == 2.0

    # Disadvantages (×0.5)
    def test_grass_loses_to_fire(self):
        assert GameEngine.elemental_multiplier("fire", "grass") == 0.5

    def test_water_loses_to_grass(self):
        assert GameEngine.elemental_multiplier("grass", "water") == 0.5

    def test_fire_loses_to_water(self):
        assert GameEngine.elemental_multiplier("water", "fire") == 0.5

    # Same element (×1.0)
    def test_fire_vs_fire(self):
        assert GameEngine.elemental_multiplier("fire", "fire") == 1.0

    def test_water_vs_water(self):
        assert GameEngine.elemental_multiplier("water", "water") == 1.0

    def test_grass_vs_grass(self):
        assert GameEngine.elemental_multiplier("grass", "grass") == 1.0


# ---------------------------------------------------------------------------
# resolve_battle
# ---------------------------------------------------------------------------

class TestResolveBattle:
    def test_advantage_doubles_played_value(self):
        # played fire (value 6) vs onboard grass (value 4)
        # effective = 6×2 = 12, points = 12−4 = 8
        points = GameEngine.resolve_battle(card(4, "grass"), card(6, "fire"))
        assert points == 8.0

    def test_disadvantage_halves_played_value(self):
        # played grass (value 6) vs onboard fire (value 4)
        # effective = 6×0.5 = 3, points = 3−4 = −1
        points = GameEngine.resolve_battle(card(4, "fire"), card(6, "grass"))
        assert points == -1.0

    def test_same_element_no_multiplier(self):
        # played water (5) vs onboard water (5) → 5−5 = 0
        points = GameEngine.resolve_battle(card(5, "water"), card(5, "water"))
        assert points == 0.0

    def test_negative_points_possible(self):
        # played water (1) vs onboard water (8) → 1−8 = −7
        points = GameEngine.resolve_battle(card(8, "water"), card(1, "water"))
        assert points == -7.0

    def test_advantage_with_min_values(self):
        # played fire (1) vs onboard grass (1) → 1×2−1 = 1
        points = GameEngine.resolve_battle(card(1, "grass"), card(1, "fire"))
        assert points == 1.0

    def test_advantage_with_max_values(self):
        # played fire (8) vs onboard grass (8) → 8×2−8 = 8
        points = GameEngine.resolve_battle(card(8, "grass"), card(8, "fire"))
        assert points == 8.0


# ---------------------------------------------------------------------------
# next_turn_state
# ---------------------------------------------------------------------------

class TestNextTurnState:
    def test_turn1_moves_to_turn2_same_round(self):
        state = GameEngine.next_turn_state(current_turn=1, current_round=1, max_rounds=5)
        assert state["turn"] == 2
        assert state["round"] == 1
        assert state["round_complete"] is False
        assert state["game_over"] is False

    def test_turn2_completes_round_and_advances(self):
        state = GameEngine.next_turn_state(current_turn=2, current_round=1, max_rounds=5)
        assert state["turn"] == 1
        assert state["round"] == 2
        assert state["round_complete"] is True
        assert state["game_over"] is False

    def test_turn2_on_last_round_ends_game(self):
        state = GameEngine.next_turn_state(current_turn=2, current_round=5, max_rounds=5)
        assert state["game_over"] is True
        assert state["round_complete"] is True

    def test_turn2_before_last_round_not_over(self):
        state = GameEngine.next_turn_state(current_turn=2, current_round=4, max_rounds=5)
        assert state["game_over"] is False


# ---------------------------------------------------------------------------
# is_game_over
# ---------------------------------------------------------------------------

class TestIsGameOver:
    def test_not_over_mid_game(self):
        hands = [[card(3, "fire"), card(5, "water")], [card(2, "grass")]]
        assert GameEngine.is_game_over(2, 5, hands) is False

    def test_over_when_rounds_exhausted(self):
        hands = [[card(3, "fire")], [card(2, "grass")]]
        assert GameEngine.is_game_over(6, 5, hands) is True

    def test_over_when_player_has_empty_hand(self):
        hands = [[card(3, "fire")], []]
        assert GameEngine.is_game_over(2, 5, hands) is True

    def test_over_on_exact_round_boundary(self):
        # round == max_rounds is still in progress; round > max_rounds ends it
        hands = [[card(1, "fire")], [card(1, "water")]]
        assert GameEngine.is_game_over(5, 5, hands) is False
        assert GameEngine.is_game_over(6, 5, hands) is True


# ---------------------------------------------------------------------------
# determine_winner
# ---------------------------------------------------------------------------

class TestDetermineWinner:
    def test_clear_winner(self):
        assert GameEngine.determine_winner({1: 20.0, 2: 15.0}) == 1

    def test_draw_returns_none(self):
        assert GameEngine.determine_winner({1: 10.0, 2: 10.0}) is None

    def test_single_player(self):
        assert GameEngine.determine_winner({1: 5.0}) == 1

    def test_empty_returns_none(self):
        assert GameEngine.determine_winner({}) is None

    def test_winner_with_negative_points(self):
        # Both negative — higher (less negative) wins
        assert GameEngine.determine_winner({1: -2.0, 2: -8.0}) == 1


# ---------------------------------------------------------------------------
# deal_hand / random_card — structural checks
# ---------------------------------------------------------------------------

class TestCardCreation:
    def test_random_card_has_required_fields(self):
        c = GameEngine.random_card()
        assert "value" in c
        assert "element" in c

    def test_random_card_value_in_range(self):
        for _ in range(50):
            c = GameEngine.random_card(min_value=2, max_value=6)
            assert 2 <= c["value"] <= 6

    def test_random_card_element_valid(self):
        for _ in range(50):
            c = GameEngine.random_card()
            assert c["element"] in ELEMENTS

    def test_deal_hand_correct_size(self):
        hand = GameEngine.deal_hand(5)
        assert len(hand) == 5

    def test_deal_hand_all_valid_cards(self):
        hand = GameEngine.deal_hand(10, min_value=1, max_value=8)
        for c in hand:
            assert c["element"] in ELEMENTS
            assert 1 <= c["value"] <= 8

    def test_deal_hand_seeded_deterministic(self):
        random.seed(42)
        hand_a = GameEngine.deal_hand(5)
        random.seed(42)
        hand_b = GameEngine.deal_hand(5)
        assert hand_a == hand_b
