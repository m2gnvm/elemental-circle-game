from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum


class ElementType(enum.Enum):
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
    element = Column(Enum(ElementType), nullable=False)
    
    def __repr__(self):
        return f"Card(value={self.value}, element={self.element.value})"



