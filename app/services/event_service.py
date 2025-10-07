"""Event service for logging game events to PostgreSQL"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from app.models.events import GameEvent, GameResult, PlayerStats
from app.models.user import User
from app.models.game import Game

class EventService:
    """Service for logging game events and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_game_created(self, game_id: int, max_rounds: int) -> None:
        """Log game creation event"""
        event = GameEvent(
            game_id=game_id,
            event_type="game_created",
            data={"max_rounds": max_rounds}
        )
        self.db.add(event)
        self.db.commit()
    
    def log_round_started(self, game_id: int, round_number: int) -> None:
        """Log round start event"""
        event = GameEvent(
            game_id=game_id,
            event_type="round_started",
            data={"round": round_number}
        )
        self.db.add(event)
        self.db.commit()
    
    def log_card_played(self, game_id: int, player_id: int, card: Dict[str, Any], 
                       points: int, is_onboard: bool) -> None:
        """Log card played event"""
        event = GameEvent(
            game_id=game_id,
            player_id=player_id,
            event_type="card_played",
            data={
                "card": card,
                "points": points,
                "is_onboard": is_onboard
            }
        )
        self.db.add(event)
        self.db.commit()
    
    def log_round_ended(self, game_id: int, round_number: int, 
                        player_points: Dict[int, int]) -> None:
        """Log round end event"""
        event = GameEvent(
            game_id=game_id,
            event_type="round_ended",
            data={
                "round": round_number,
                "player_points": player_points
            }
        )
        self.db.add(event)
        self.db.commit()
    
    def log_game_finished(self, game_id: int, final_results: List[Dict[str, Any]]) -> None:
        """Log game finished event and save results"""
        # Log the event
        event = GameEvent(
            game_id=game_id,
            event_type="game_finished",
            data={"final_results": final_results}
        )
        self.db.add(event)
        
        # Save game results
        for i, result in enumerate(final_results, 1):
            game_result = GameResult(
                game_id=game_id,
                player_id=result["player_id"],
                final_points=result["points"],
                position=i,
                cards_played=result["cards_played"]
            )
            self.db.add(game_result)
        
        # Update player statistics
        self._update_player_stats(final_results)
        
        self.db.commit()
    
    def _update_player_stats(self, final_results: List[Dict[str, Any]]) -> None:
        """Update player statistics"""
        for result in final_results:
            player_id = result["player_id"]
            points = result["points"]
            is_winner = result["position"] == 1
            
            # Get or create player stats
            stats = self.db.query(PlayerStats).filter(
                PlayerStats.player_id == player_id
            ).first()
            
            if not stats:
                stats = PlayerStats(player_id=player_id)
                self.db.add(stats)
            
            # Update stats
            stats.games_played += 1
            if is_winner:
                stats.games_won += 1
            stats.total_points += points
            stats.average_points = stats.total_points / stats.games_played
    
    def get_player_stats(self, player_id: int) -> Optional[PlayerStats]:
        """Get player statistics"""
        return self.db.query(PlayerStats).filter(
            PlayerStats.player_id == player_id
        ).first()
    
    def get_game_events(self, game_id: int) -> List[GameEvent]:
        """Get all events for a game"""
        return self.db.query(GameEvent).filter(
            GameEvent.game_id == game_id
        ).order_by(GameEvent.created_at).all()
    
    def get_recent_games(self, limit: int = 10) -> List[Game]:
        """Get recent finished games"""
        return self.db.query(Game).filter(
            Game.status == "finished"
        ).order_by(Game.updated_at.desc()).limit(limit).all()
    
    def get_leaderboard(self, limit: int = 10) -> List[PlayerStats]:
        """Get leaderboard by average points"""
        return self.db.query(PlayerStats).order_by(
            PlayerStats.average_points.desc()
        ).limit(limit).all()
