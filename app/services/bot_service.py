"""
BotService — server-side AI opponent for vs-bot games.

Bot design:
  - Turn 1 (sets board): plays its highest-value card (hardest for human to score against)
  - Turn 2 (counter): plays the card that maximises resolve_battle points

The bot user is a regular User row with username "ElementalBot".  It is
created automatically on first use; no manual seeding is required.
"""
from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.engine.game_engine import GameEngine
from app.models.game import GamePlayer
from app.models.user import User

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

BOT_USERNAME = "ElementalBot"
BOT_EMAIL = "bot@elemental.internal"
_BOT_PASSWORD = "internal-bot-only-not-for-login-2024"


class BotService:

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    @staticmethod
    def get_or_create_bot_user(db: Session) -> User:
        """Return the bot's User row, creating it if it doesn't exist."""
        bot = db.query(User).filter(User.username == BOT_USERNAME).first()
        if bot:
            return bot

        bot = User(
            username=BOT_USERNAME,
            email=BOT_EMAIL,
            hashed_password=_pwd_context.hash(_BOT_PASSWORD),
            is_active=True,
        )
        db.add(bot)
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def get_bot_player(game_id: int, db: Session) -> GamePlayer | None:
        """Return the bot's GamePlayer for a game, or None if no bot."""
        return (
            db.query(GamePlayer)
            .join(User, GamePlayer.user_id == User.id)
            .filter(
                GamePlayer.game_id == game_id,
                User.username == BOT_USERNAME,
            )
            .first()
        )

    # ------------------------------------------------------------------
    # Card selection strategy
    # ------------------------------------------------------------------

    @staticmethod
    def is_bot_turn(game_state: dict, bot_player_id: int) -> bool:
        """
        Return True when the bot should play next.

        board_setter (turn 1) ← plays the board card, earns no points.
        counter     (turn 2) ← responds to the board card, earns points.

        The bot's role alternates each round via board_setter_player_id.
        """
        board_setter = game_state.get("board_setter_player_id")
        if board_setter is None:
            return False
        turn = game_state.get("turn", 1)
        bot_is_setter = int(board_setter) == bot_player_id
        return (turn == 1 and bot_is_setter) or (turn == 2 and not bot_is_setter)

    @staticmethod
    def choose_card_index(
        hand: list[dict],
        onboard_card: dict | None,
        turn: int,
    ) -> int:
        """
        Pick the best card index from the bot's hand.

        turn=1 (setting board): play the highest-value card.
            A high board value forces the human to need element advantage
            to score positively.

        turn=2 (countering): play the card that maximises resolve_battle.
        """
        if not hand:
            return 0

        if turn == 1 or onboard_card is None:
            return max(range(len(hand)), key=lambda i: hand[i]["value"])

        return max(
            range(len(hand)),
            key=lambda i: GameEngine.resolve_battle(onboard_card, hand[i]),
        )
