"""Game Events Models - PostgreSQL for persistent events"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class GameEvent(Base):
    """Game events for analytics and history"""
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # 'game_created', 'round_started', 'card_played', 'round_ended', 'game_finished'
    player_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for system events
    data = Column(JSON)  # event-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    game = relationship("Game", back_populates="events")
    player = relationship("User", back_populates="game_events")


class GameResult(Base):
    """Final game results"""
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    final_points = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)  # 1st, 2nd place
    cards_played = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    game = relationship("Game", back_populates="results")
    player = relationship("User", back_populates="game_results")


class PlayerStats(Base):
    """Player statistics (aggregated)"""
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    average_points = Column(DECIMAL(5, 2), default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    player = relationship("User", back_populates="stats")
