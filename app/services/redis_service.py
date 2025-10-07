"""Redis service for fast game state management"""

import json
import redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.core.config import settings

class RedisGameService:
    """Redis-based game state management"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    def create_game_state(self, game_id: int, max_rounds: int = 5) -> Dict[str, Any]:
        """Create initial game state in Redis"""
        game_state = {
            "status": "waiting",
            "round": 1,
            "turn": 1,
            "max_rounds": max_rounds,
            "onboard_card": None,
            "players": {},
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        key = f"game:{game_id}"
        self.redis_client.setex(key, timedelta(hours=24), json.dumps(game_state))
        return game_state
    
    def get_game_state(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get game state from Redis"""
        key = f"game:{game_id}"
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def update_game_state(self, game_id: int, updates: Dict[str, Any]) -> bool:
        """Update game state in Redis"""
        key = f"game:{game_id}"
        
        # Get current state
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        # Update state
        current_state.update(updates)
        current_state["last_activity"] = datetime.utcnow().isoformat()
        
        # Save back to Redis
        self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
        return True
    
    def add_player(self, game_id: int, player_id: int, username: str, hand: List[Dict]) -> bool:
        """Add player to game state"""
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        # Add player to existing players
        current_state["players"][str(player_id)] = {
            "id": player_id,
            "username": username,
            "points": 0,
            "hand": hand,
            "cards_played": 0
        }
        current_state["last_activity"] = datetime.utcnow().isoformat()
        
        # Save back to Redis
        key = f"game:{game_id}"
        self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
        return True
    
    def update_player_hand(self, game_id: int, player_id: int, new_hand: List[Dict]) -> bool:
        """Update player's hand"""
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        if str(player_id) in current_state["players"]:
            current_state["players"][str(player_id)]["hand"] = new_hand
            current_state["last_activity"] = datetime.utcnow().isoformat()
            
            key = f"game:{game_id}"
            self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
            return True
        return False
    
    def update_player_points(self, game_id: int, player_id: int, points: int) -> bool:
        """Update player's points"""
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        if str(player_id) in current_state["players"]:
            current_state["players"][str(player_id)]["points"] += points
            current_state["last_activity"] = datetime.utcnow().isoformat()
            
            key = f"game:{game_id}"
            self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
            return True
        return False
    
    def set_onboard_card(self, game_id: int, card: Dict[str, Any]) -> bool:
        """Set the onboard card"""
        updates = {"onboard_card": card}
        return self.update_game_state(game_id, updates)
    
    def increment_turn(self, game_id: int) -> bool:
        """Increment turn counter"""
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        current_state["turn"] += 1
        current_state["last_activity"] = datetime.utcnow().isoformat()
        
        key = f"game:{game_id}"
        self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
        return True
    
    def next_round(self, game_id: int) -> bool:
        """Move to next round"""
        current_state = self.get_game_state(game_id)
        if not current_state:
            return False
        
        current_state["round"] += 1
        current_state["turn"] = 1
        current_state["last_activity"] = datetime.utcnow().isoformat()
        
        key = f"game:{game_id}"
        self.redis_client.setex(key, timedelta(hours=24), json.dumps(current_state))
        return True
    
    def finish_game(self, game_id: int) -> bool:
        """Mark game as finished"""
        updates = {"status": "finished"}
        return self.update_game_state(game_id, updates)
    
    def delete_game(self, game_id: int) -> bool:
        """Delete game from Redis"""
        key = f"game:{game_id}"
        return self.redis_client.delete(key) > 0
    
    def get_active_games(self) -> List[int]:
        """Get list of active game IDs"""
        pattern = "game:*"
        keys = self.redis_client.keys(pattern)
        game_ids = []
        for key in keys:
            if key.startswith("game:"):
                game_id = key.split(":")[1]
                game_ids.append(int(game_id))
        return game_ids
    
    def cleanup_expired_games(self) -> int:
        """Clean up expired games (older than 24 hours)"""
        # Redis TTL will handle this automatically
        # This method is for manual cleanup if needed
        active_games = self.get_active_games()
        cleaned = 0
        
        for game_id in active_games:
            state = self.get_game_state(game_id)
            if state and state.get("status") == "finished":
                # Check if game is older than 24 hours
                created_at = datetime.fromisoformat(state["created_at"])
                if datetime.utcnow() - created_at > timedelta(hours=24):
                    self.delete_game(game_id)
                    cleaned += 1
        
        return cleaned
