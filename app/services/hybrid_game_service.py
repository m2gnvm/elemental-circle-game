"""Hybrid game service using Redis for state and PostgreSQL for events"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from app.models.game import Game, GamePlayer
from app.services.redis_service import RedisGameService
from app.services.event_service import EventService
from app.engine.game_engine import GameEngine
from app.core.config import settings
import random
import secrets

class HybridGameService:
    """Hybrid game service using Redis for fast state and PostgreSQL for persistence"""

    def __init__(self, db: Session):
        self.db = db
        self.redis_service = RedisGameService()
        self.event_service = EventService(db)
    
    def create_game(self, room_code: str, max_rounds: int = 5) -> Game:
        """Create a new game room"""
        # Create game in PostgreSQL
        game = Game(
            room_code=room_code,
            status="waiting",
            max_rounds=max_rounds
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        
        # Create game state in Redis
        self.redis_service.create_game_state(game.id, max_rounds)
        
        # Log event
        self.event_service.log_game_created(game.id, max_rounds)
        
        return game
    
    def join_game(self, game_id: int, user_id: int) -> GamePlayer:
        """Join a game"""
        # Create player in PostgreSQL
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        # Get player number
        existing_players = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id
        ).count()
        
        player = GamePlayer(
            game_id=game_id,
            user_id=user_id,
            player_number=existing_players + 1,
            is_ready=True
        )
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        
        return player
    
    def start_game(self, game_id: int) -> bool:
        """Start the game"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False
        
        # Update PostgreSQL
        game.status = "in_progress"
        self.db.commit()

        # Sync status to Redis — get_game_state reads Redis, not PostgreSQL
        self.redis_service.update_game_state(game_id, {"status": "in_progress"})

        # Deal cards and update Redis
        players = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
        
        for player in players:
            hand = GameEngine.deal_hand(
                settings.CARDS_PER_PLAYER,
                settings.MIN_CARD_VALUE,
                settings.MAX_CARD_VALUE,
            )
            self.redis_service.add_player(
                game_id,
                player.id,
                player.user.username,
                hand,
                user_id=player.user_id,
            )

        # Set initial onboard card
        initial_card = GameEngine.random_card(settings.MIN_CARD_VALUE, settings.MAX_CARD_VALUE)
        self.redis_service.set_onboard_card(game_id, initial_card)

        # Coin flip — randomly pick which player sets the board first.
        # This same mechanic works for both multiplayer and vs-bot games.
        first_setter_id = random.choice([p.id for p in players])
        self.redis_service.update_game_state(
            game_id, {"board_setter_player_id": first_setter_id}
        )

        # Log round start
        self.event_service.log_round_started(game_id, 1)

        return first_setter_id  # callers may use this to know who goes first
    
    def play_card(self, game_id: int, player_id: int, card_index: int) -> Dict[str, Any]:
        """Play a card and calculate the result"""
        # Get game state from Redis
        game_state = self.redis_service.get_game_state(game_id)
        if not game_state:
            raise ValueError("Game not found in Redis")
        
        # Get player data
        player_data = game_state["players"].get(str(player_id))
        if not player_data:
            raise ValueError("Player not found in game")
        
        # Enforce whose turn it is.
        # board_setter_player_id = the GamePlayer.id that plays turn 1 this round.
        # The other player plays turn 2. Reject plays that are out of order.
        board_setter = game_state.get("board_setter_player_id")
        if board_setter is not None:
            is_setter = int(board_setter) == player_id
            current_turn = game_state["turn"]
            if is_setter and current_turn != 1:
                raise ValueError("Not your turn — wait for the other player to set the board")
            if not is_setter and current_turn != 2:
                raise ValueError("Not your turn — the other player must set the board first")

        # Get card from hand
        hand = player_data["hand"]
        if card_index >= len(hand):
            raise ValueError("Invalid card index")

        played_card = hand[card_index]

        # Get onboard card
        onboard_card = game_state["onboard_card"]
        if not onboard_card:
            raise ValueError("No onboard card found")
        
        # Calculate battle result
        points = GameEngine.resolve_battle(onboard_card, played_card)
        
        # Advance turn / round state
        turn_state = GameEngine.next_turn_state(
            current_turn=game_state["turn"],
            current_round=game_state["round"],
            max_rounds=game_state["max_rounds"],
        )

        updates: dict[str, Any] = {
            "turn": turn_state["turn"],
            "round": turn_state["round"],
        }

        # Only the counter-player (turn 2) scores points
        if game_state["turn"] == 2:
            self.redis_service.update_player_points(game_id, player_id, points)

            # Flip board-setter for the next round
            all_ids = [int(pid) for pid in game_state["players"]]
            current_setter = game_state.get("board_setter_player_id")
            if current_setter is not None and len(all_ids) == 2:
                updates["board_setter_player_id"] = next(
                    pid for pid in all_ids if pid != int(current_setter)
                )

            # Log round end
            player_points = {
                int(pid): pdata["points"]
                for pid, pdata in game_state["players"].items()
            }
            self.event_service.log_round_ended(game_id, game_state["round"], player_points)

            if turn_state["game_over"]:
                updates["status"] = "finished"
                self._finish_game(game_id)
        
        # Update onboard card
        self.redis_service.set_onboard_card(game_id, played_card)
        
        # Remove card from hand
        new_hand = [card for i, card in enumerate(hand) if i != card_index]
        self.redis_service.update_player_hand(game_id, player_id, new_hand)
        
        # Update game state
        self.redis_service.update_game_state(game_id, updates)
        
        # Log card played event — use user_id (FK to users), not GamePlayer.id
        user_id_for_event = player_data.get("user_id")
        self.event_service.log_card_played(
            game_id, user_id_for_event, played_card, points, game_state["turn"] == 1
        )
        
        # Check empty-hand game-over (separate from round-exhaustion above)
        updated_state = self.redis_service.get_game_state(game_id)
        if updated_state.get("status") != "finished":
            hands = [pdata["hand"] for pdata in updated_state["players"].values()]
            if GameEngine.is_game_over(updated_state["round"], updated_state["max_rounds"], hands):
                updates["status"] = "finished"
                self.redis_service.update_game_state(game_id, {"status": "finished"})
                self._finish_game(game_id)
                updated_state = self.redis_service.get_game_state(game_id)

        awarded = points if game_state["turn"] == 2 else 0
        return {
            "points": awarded,
            "player_points": player_data["points"] + awarded,
            "onboard_card": played_card,
            "game_finished": updated_state.get("status") == "finished",
            "round": updated_state["round"],
            "turn": updated_state["turn"],
        }
    
    def get_game_state(self, game_id: int, player_id: int = None) -> Optional[Dict[str, Any]]:
        """Get game state from Redis"""
        game_state = self.redis_service.get_game_state(game_id)
        if not game_state:
            return None
        
        # Convert to API format
        players = []
        for pid, pdata in game_state["players"].items():
            players.append({
                "id": pdata["id"],
                "username": pdata["username"],
                "points": pdata["points"],
                "cards_in_hand": len(pdata["hand"])
            })
        
        result = {
            "game_id": game_id,
            "status": game_state["status"],
            "round": game_state["round"],
            "turn": game_state["turn"],
            "onboard_card": game_state["onboard_card"],
            "players": players
        }
        
        # Add player's hand if requested
        if player_id:
            player_data = game_state["players"].get(str(player_id))
            if player_data:
                result["your_hand"] = player_data["hand"]
        
        return result
    
    def _finish_game(self, game_id: int) -> None:
        """Finish the game, determine winner, and persist results."""
        game_state = self.redis_service.get_game_state(game_id)
        if not game_state:
            return

        player_points = {
            pdata["id"]: pdata["points"]
            for pdata in game_state["players"].values()
        }
        winner_id = GameEngine.determine_winner(player_points)

        game = self.db.query(Game).filter(Game.id == game_id).first()
        if game:
            game.status = "finished"
            self.db.commit()

        final_results = sorted(
            [
                {
                    "player_id": pdata["id"],
                    "points": pdata["points"],
                    "cards_played": pdata.get("cards_played", 0),
                }
                for pdata in game_state["players"].values()
            ],
            key=lambda x: x["points"],
            reverse=True,
        )

        self.event_service.log_game_finished(game_id, final_results)
    
    def cleanup_expired_games(self) -> int:
        """Clean up expired games"""
        return self.redis_service.cleanup_expired_games()
    
    def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get player statistics"""
        stats = self.event_service.get_player_stats(player_id)
        if stats:
            return {
                "games_played": stats.games_played,
                "games_won": stats.games_won,
                "total_points": stats.total_points,
                "average_points": float(stats.average_points),
                "win_rate": stats.games_won / stats.games_played if stats.games_played > 0 else 0
            }
        return None
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard"""
        stats = self.event_service.get_leaderboard(limit)
        return [
            {
                "player_id": stat.player_id,
                "username": stat.player.username,
                "games_played": stat.games_played,
                "games_won": stat.games_won,
                "average_points": float(stat.average_points),
                "win_rate": stat.games_won / stat.games_played if stat.games_played > 0 else 0
            }
            for stat in stats
        ]
