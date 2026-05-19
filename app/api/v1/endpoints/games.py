from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.hybrid_game_service import HybridGameService
from app.services.bot_service import BotService
from app.models.user import User
from app.models.game import Game, GamePlayer
from app.api.v1.endpoints.auth import get_current_user
from pydantic import BaseModel
import secrets

router = APIRouter()


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
        first_setter_id = game_service.start_game(game_id)
        if first_setter_id is None:
            raise HTTPException(status_code=400, detail="Failed to start game")
        game = db.query(Game).filter(Game.id == game_id).first()
        return {
            "game_id": game.id,
            "status": game.status,
            "message": "Game started successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/vs-bot")
async def create_vs_bot_game(
    request: CreateGameRequest = CreateGameRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a game against the AI bot and start it immediately."""
    game_service = HybridGameService(db)
    room_code = secrets.token_urlsafe(8)

    game = game_service.create_game(room_code, request.max_rounds)

    # Join human first, then bot
    human_player = game_service.join_game(game.id, current_user.id)
    bot_user = BotService.get_or_create_bot_user(db)
    bot_player = game_service.join_game(game.id, bot_user.id)

    # start_game handles coin flip and sets board_setter_player_id in Redis —
    # exactly the same mechanic as a regular multiplayer game.
    first_setter_id = game_service.start_game(game.id)

    # If the bot won the coin flip, let it play turn 1 immediately
    if first_setter_id == bot_player.id:
        _bot_play(game_id=game.id, bot_player_id=bot_player.id, game_service=game_service)

    you_go_first = (first_setter_id == human_player.id)

    return {
        "game_id": game.id,
        "room_code": game.room_code,
        "player_id": human_player.id,
        "status": "in_progress",
        "vs_bot": True,
        "max_rounds": game.max_rounds,
        "you_go_first": you_go_first,
    }


@router.post("/{game_id}/play")
async def play_card(
    game_id: int,
    card_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Play a card in the game."""
    game_service = HybridGameService(db)

    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id,
    ).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found in this game")

    try:
        result = game_service.play_card(game_id, player.id, card_index)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Keep playing for the bot as long as it's the bot's turn.
    # This handles two consecutive bot turns that happen at a round boundary:
    #   1. Bot counters (turn 2) — round ends, board_setter flips to bot
    #   2. Bot immediately sets the board (turn 1 of new round)
    # We loop until the state requires the human to act.
    if not result["game_finished"]:
        bot_player = BotService.get_bot_player(game_id, db)
        if bot_player:
            state = game_service.redis_service.get_game_state(game_id)
            while (
                state
                and state.get("status") != "finished"
                and BotService.is_bot_turn(state, bot_player.id)
            ):
                _bot_play(
                    game_id=game_id,
                    bot_player_id=bot_player.id,
                    game_service=game_service,
                )
                state = game_service.redis_service.get_game_state(game_id)

            # Refresh result fields so client sees state after all bot plays
            updated = game_service.get_game_state(game_id, player.id)
            if updated:
                result["round"] = updated["round"]
                result["turn"] = updated["turn"]
                result["game_finished"] = updated["status"] == "finished"

    return result


def _bot_play(game_id: int, bot_player_id: int, game_service: HybridGameService) -> None:
    """Play one card for the bot. Silently skips if game is over or hand is empty."""
    try:
        state = game_service.redis_service.get_game_state(game_id)
        if not state or state.get("status") == "finished":
            return
        bot_data = state["players"].get(str(bot_player_id))
        if not bot_data or not bot_data["hand"]:
            return
        idx = BotService.choose_card_index(
            bot_data["hand"],
            state.get("onboard_card"),
            state["turn"],
        )
        game_service.play_card(game_id, bot_player_id, idx)
    except Exception:
        pass  # Never crash a human request due to bot error


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
            "created_at": game.created_at,
        }
        for game in games
    ]


@router.get("/{game_id}/state")
async def get_game_state(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current game state"""
    game_service = HybridGameService(db)

    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id,
    ).first()

    if not player:
        raise HTTPException(status_code=403, detail="You are not in this game")

    state = game_service.get_game_state(game_id, player.id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")

    return state


