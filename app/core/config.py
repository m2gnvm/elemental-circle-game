from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://gameuser:gamepass123@localhost/elemental_circle"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-elemental-circle-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Hardcoded — backend is internal-only (Nginx proxies to it).
    # Excluded from env parsing to avoid JSON format issues across platforms.
    ALLOWED_HOSTS: List[str] = Field(default=["*"], exclude=True)

    # Game Settings
    MAX_PLAYERS_PER_GAME: int = 2
    CARDS_PER_PLAYER: int = 5
    MAX_CARD_VALUE: int = 8
    MIN_CARD_VALUE: int = 1

    class Config:
        env_file = "local.env"


settings = Settings()
