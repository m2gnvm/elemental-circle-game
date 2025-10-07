import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.game import Game, GamePlayer
from app.models.card import ElementType
from app.core.config import settings


class GameService:
    def __init__(self, db: Session):
        self.db = db

    def create_game(self, room_code: str, max_rounds: int = 5) -> Game:
        """Create a new game room"""
        game = Game(
            room_code=room_code,
            status="waiting",
            max_rounds=max_rounds,
            game_state=self._get_initial_game_state()
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def join_game(self, game_id: int, user_id: int) -> GamePlayer:
        """Add a player to the game"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        if len(game.players) >= settings.MAX_PLAYERS_PER_GAME:
            raise ValueError("Game is full")
        
        player_number = len(game.players) + 1
        player = GamePlayer(
            game_id=game_id,
            user_id=user_id,
            player_number=player_number,
            hand=[]
        )
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def start_game(self, game_id: int) -> Game:
        """Start the game and deal cards"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        if len(game.players) != settings.MAX_PLAYERS_PER_GAME:
            raise ValueError("Not enough players")
        
        # Deal cards to each player
        for player in game.players:
            hand = self._deal_cards()
            player.hand = hand
            self.db.add(player)
        
        # Create initial onboard card
        onboard_card = self._create_random_card()
        game_card = GameCard(
            game_id=game_id,
            card_value=onboard_card["value"],
            card_element=onboard_card["element"],
            position="onboard"
        )
        self.db.add(game_card)
        
        game.status = "in_progress"
        game.game_state = self._get_initial_game_state()
        self.db.commit()
        self.db.refresh(game)
        return game

    def play_card(self, game_id: int, player_id: int, card_index: int) -> Dict[str, Any]:
        """Play a card and calculate the result"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        player = self.db.query(GamePlayer).filter(
            GamePlayer.id == player_id,
            GamePlayer.game_id == game_id
        ).first()
        
        if not game or not player:
            raise ValueError("Game or player not found")
        
        if game.status != "in_progress":
            raise ValueError("Game is not in progress")
        
        # Get the card from player's hand
        if card_index >= len(player.hand):
            raise ValueError("Invalid card index")
        
        played_card = player.hand[card_index]
        
        # Get current onboard card
        onboard_card = self.db.query(GameCard).filter(
            GameCard.game_id == game_id,
            GameCard.position == "onboard"
        ).first()
        
        if not onboard_card:
            raise ValueError("No onboard card found")
        
        # Calculate battle result
        points = self._battle_cards(
            {"value": onboard_card.card_value, "element": onboard_card.card_element},
            played_card
        )
        
        # Only the counter player gets points
        # Turn 1 = onboard player (no points)
        # Turn 2 = counter player (gets points)
        actual_points_awarded = 0
        if game.current_turn == 2:
            player.points += points
            actual_points_awarded = points
        
        # Remove card from hand
        player.hand.pop(card_index)
        
        # Update onboard card
        onboard_card.card_value = played_card["value"]
        onboard_card.card_element = played_card["element"]
        
        # Check if round is finished (both players have played)
        if game.current_turn >= 2:  # Both players have played
            game.round_number += 1
            game.current_turn = 1
            
            # Check if game is finished (max rounds reached)
            if game.round_number > game.max_rounds:
                game.status = "finished"
        else:
            game.current_turn += 1
        
        # Check if any player has no cards left (after turn increment)
        for game_player in game.players:
            if len(game_player.hand) == 0:
                game.status = "finished"
                break
        
        self.db.commit()
        self.db.refresh(player)
        
        return {
            "points": actual_points_awarded,
            "player_points": player.points,
            "onboard_card": {"value": onboard_card.card_value, "element": onboard_card.card_element},
            "game_finished": game.status == "finished",
            "round": game.round_number,
            "turn": game.current_turn
        }

    def _battle_cards(self, onboard_card: Dict, played_card: Dict) -> float:
        """Calculate battle result
        Apply elemental multiplier to card values before comparing
        """
        multiplier = self._get_elemental_multiplier(
            onboard_card["element"], 
            played_card["element"]
        )
        
        # Apply multiplier to played card value
        effective_played_value = played_card["value"] * multiplier
        
        # Calculate points (effective played value - onboard value)
        points = effective_played_value - onboard_card["value"]
        
        return points

    def _get_elemental_multiplier(self, onboard_element: str, played_element: str) -> float:
        """Get elemental advantage multiplier
        Grass > Water > Fire > Grass
        """
        if played_element == onboard_element:
            return 1.0
        elif ((played_element == "grass" and onboard_element == "water") or
              (played_element == "water" and onboard_element == "fire") or
              (played_element == "fire" and onboard_element == "grass")):
            return 2.0  # Played element has advantage
        else:
            return 0.5  # Played element has disadvantage

    def _deal_cards(self) -> List[Dict[str, Any]]:
        """Deal random cards to a player"""
        cards = []
        for _ in range(settings.CARDS_PER_PLAYER):
            cards.append(self._create_random_card())
        return cards

    def _create_random_card(self) -> Dict[str, Any]:
        """Create a random card"""
        return {
            "value": random.randint(settings.MIN_CARD_VALUE, settings.MAX_CARD_VALUE),
            "element": random.choice([e.value for e in ElementType])
        }

    def _get_initial_game_state(self) -> Dict[str, Any]:
        """Get initial game state"""
        return {
            "round": 1,
            "turn": 1,
            "players": [],
            "onboard_card": None
        }


