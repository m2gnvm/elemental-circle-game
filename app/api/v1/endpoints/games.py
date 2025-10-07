from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.hybrid_game_service import HybridGameService
from app.models.user import User
from app.models.game import Game, GamePlayer
from app.api.v1.endpoints.auth import get_current_user
import secrets

router = APIRouter()


from pydantic import BaseModel

class CreateGameRequest(BaseModel):
    max_rounds: int = 5

@router.post("/create")
async def create_game(request: CreateGameRequest = CreateGameRequest(), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new game room"""
    game_service = HybridGameService(db)
    
    # Generate unique room code
    room_code = secrets.token_urlsafe(8)
    
    game = game_service.create_game(room_code, request.max_rounds)
    
    # Add creator as first player
    player = game_service.join_game(game.id, current_user.id)
    
    return {
        "game_id": game.id,
        "room_code": game.room_code,
        "player_id": player.id,
        "status": game.status,
        "max_rounds": game.max_rounds
    }


@router.post("/join/{room_code}")
async def join_game(room_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Join an existing game by room code"""
    game_service = HybridGameService(db)
    
    # Find game by room code
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Game is not accepting new players")
    
    try:
        player = game_service.join_game(game.id, current_user.id)
        return {
            "game_id": game.id,
            "room_code": game.room_code,
            "player_id": player.id,
            "status": game.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{game_id}/start")
async def start_game(game_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Start a game"""
    game_service = HybridGameService(db)
    
    try:
        success = game_service.start_game(game_id)
        if success:
            # Get the updated game
            game = db.query(Game).filter(Game.id == game_id).first()
            return {
                "game_id": game.id,
                "status": game.status,
                "message": "Game started successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start game")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{game_id}/play")
async def play_card(
    game_id: int, 
    card_index: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Play a card in the game"""
    game_service = HybridGameService(db)
    
    # Find player in this game
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found in this game")
    
    try:
        result = game_service.play_card(game_id, player.id, card_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{game_id}/state")
async def get_game_state(game_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current game state"""
    game_service = HybridGameService(db)
    
    # Check if user is in this game
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=403, detail="You are not in this game")
    
    # Get game state from Redis
    state = game_service.get_game_state(game_id, player.id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return state


@router.get("/my-games")
async def get_my_games(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get games where current user is playing"""
    games = db.query(Game).join(GamePlayer).filter(
        GamePlayer.user_id == current_user.id
    ).all()
    
    return [
        {
            "game_id": game.id,
            "room_code": game.room_code,
            "status": game.status,
            "players_count": len(game.players),
            "created_at": game.created_at
        }
        for game in games
    ]


