"""
Application Configuration

Tüm environment variable'lar ve ayarlar burada tanımlanır.
Pydantic Settings ile type-safe ve validated.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings.
    
    Değerler şu sırayla okunur:
    1. Environment variables
    2. .env dosyası
    3. Default değerler
    """
    
    # ===== APP SETTINGS =====
    APP_NAME: str = "RAG Chatbot"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # ===== DATABASE =====
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # ===== AUTHENTICATION =====
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ===== REDIS =====
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ===== OPENAI =====
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-5.1"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    
    # ===== RATE LIMITING =====
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ===== LOGGING =====
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Production environment check."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL (Alembic için)."""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """Settings singleton."""
    return Settings()


settings = get_settings()
