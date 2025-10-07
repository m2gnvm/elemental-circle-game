"""Hybrid game service using Redis for state and PostgreSQL for events"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from app.models.game import Game, GamePlayer
from app.services.redis_service import RedisGameService
from app.services.event_service import EventService
from app.services.game_service import GameService
import secrets
import random

class HybridGameService:
    """Hybrid game service using Redis for fast state and PostgreSQL for persistence"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = RedisGameService()
        self.event_service = EventService(db)
        self.legacy_service = GameService(db)  # For card dealing logic
    
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
        
        # Deal cards and update Redis
        players = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
        
        for player in players:
            # Deal cards using legacy service
            hand = self.legacy_service._deal_cards()
            
            # Update Redis with player data
            self.redis_service.add_player(
                game_id, 
                player.id, 
                player.user.username, 
                hand
            )
        
        # Set initial onboard card
        initial_card = self.legacy_service._deal_cards()[0]
        self.redis_service.set_onboard_card(game_id, initial_card)
        
        # Log round start
        self.event_service.log_round_started(game_id, 1)
        
        return True
    
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
        points = self.legacy_service._battle_cards(onboard_card, played_card)
        
        # Update Redis state
        updates = {}
        
        # Only counter player gets points
        if game_state["turn"] == 2:
            # Update player points in Redis
            self.redis_service.update_player_points(game_id, player_id, points)
            updates["turn"] = 1  # Reset turn
            updates["round"] = game_state["round"] + 1  # Next round
            
            # Log round end
            player_points = {}
            for pid, pdata in game_state["players"].items():
                player_points[int(pid)] = pdata["points"]
            self.event_service.log_round_ended(game_id, game_state["round"], player_points)
            
            # Check if game finished
            if updates["round"] > game_state["max_rounds"]:
                updates["status"] = "finished"
                self._finish_game(game_id)
        else:
            updates["turn"] = game_state["turn"] + 1
        
        # Update onboard card
        self.redis_service.set_onboard_card(game_id, played_card)
        
        # Remove card from hand
        new_hand = [card for i, card in enumerate(hand) if i != card_index]
        self.redis_service.update_player_hand(game_id, player_id, new_hand)
        
        # Update game state
        self.redis_service.update_game_state(game_id, updates)
        
        # Log card played event
        self.event_service.log_card_played(
            game_id, player_id, played_card, points, game_state["turn"] == 1
        )
        
        # Check if any player has no cards
        updated_state = self.redis_service.get_game_state(game_id)
        for pid, pdata in updated_state["players"].items():
            if not pdata["hand"]:
                self._finish_game(game_id)
                break
        
        return {
            "points": points if game_state["turn"] == 2 else 0,
            "player_points": player_data["points"] + (points if game_state["turn"] == 2 else 0),
            "onboard_card": played_card,
            "game_finished": updated_state.get("status") == "finished",
            "round": updated_state["round"],
            "turn": updated_state["turn"]
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
        """Finish the game and save results"""
        # Update PostgreSQL
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if game:
            game.status = "finished"
            self.db.commit()
        
        # Get final results from Redis
        game_state = self.redis_service.get_game_state(game_id)
        if not game_state:
            return
        
        # Prepare final results
        final_results = []
        for pid, pdata in game_state["players"].items():
            final_results.append({
                "player_id": pdata["id"],
                "points": pdata["points"],
                "cards_played": pdata["cards_played"]
            })
        
        # Sort by points (descending)
        final_results.sort(key=lambda x: x["points"], reverse=True)
        
        # Log game finished
        self.event_service.log_game_finished(game_id, final_results)
        
        # Clean up Redis after some time
        # (Redis TTL will handle this automatically)
    
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
