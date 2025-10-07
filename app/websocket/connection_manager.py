from fastapi import WebSocket
from typing import List, Dict
import json


class ConnectionManager:
    def __init__(self):
        # Dictionary to store connections by game_id
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        """Accept a WebSocket connection and add it to the game room"""
        await websocket.accept()
        
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        """Remove a WebSocket connection from the game room"""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            
            # Clean up empty game rooms
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        await websocket.send_text(message)

    async def broadcast_to_game(self, game_id: str, message: str):
        """Broadcast a message to all connections in a game room"""
        if game_id in self.active_connections:
            # Create a list of connections to send to
            connections_to_send = self.active_connections[game_id].copy()
            
            for connection in connections_to_send:
                try:
                    await connection.send_text(message)
                except:
                    # Remove broken connections
                    if connection in self.active_connections[game_id]:
                        self.active_connections[game_id].remove(connection)

    async def broadcast_game_state(self, game_id: str, game_state: dict):
        """Broadcast game state update to all players in a game"""
        message = json.dumps({
            "type": "game_state_update",
            "data": game_state
        })
        await self.broadcast_to_game(game_id, message)

    async def broadcast_player_action(self, game_id: str, player_id: int, action: dict):
        """Broadcast a player action to all other players"""
        message = json.dumps({
            "type": "player_action",
            "player_id": player_id,
            "data": action
        })
        await self.broadcast_to_game(game_id, message)


