"""
Redis Connection Manager

Redis bağlantısını ve LangGraph checkpointer'ını yönetir.
"""

from typing import Optional
import redis.asyncio as redis
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings


# Redis client singleton
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Redis client singleton."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client


async def close_redis() -> None:
    """Redis bağlantısını kapat."""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# Checkpointer singleton
_checkpointer: Optional[MemorySaver] = None


def get_checkpointer() -> MemorySaver:
    """
    LangGraph checkpointer.
    
    Not: langgraph-checkpoint-redis paketi kuruluysa
    RedisSaver kullanılabilir. Şimdilik MemorySaver
    ile başlayıp Redis'i manuel state storage için kullanıyoruz.
    """
    global _checkpointer
    
    if _checkpointer is None:
        _checkpointer = MemorySaver()
    
    return _checkpointer

