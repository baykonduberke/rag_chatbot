"""
Redis Connection Manager

Redis bağlantısını ve LangGraph checkpointer'ını yönetir.
Mesaj geçmişi Redis'te saklanır (kalıcı).
"""

from typing import Optional, Union
import redis as sync_redis
import redis.asyncio as redis
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver

from app.core.config import settings


# Redis client singleton
_redis_client: Optional[redis.Redis] = None

# Sync Redis client for checkpointer
_sync_redis_client: Optional[sync_redis.Redis] = None

# Checkpointer singleton
_checkpointer: Optional[Union[RedisSaver, MemorySaver]] = None


async def get_redis_client() -> redis.Redis:
    """Redis client singleton (async)."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client


def get_sync_redis_client() -> sync_redis.Redis:
    """Redis client singleton (sync)."""
    global _sync_redis_client
    
    if _sync_redis_client is None:
        _sync_redis_client = sync_redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False  # RedisSaver için binary gerekli
        )
    
    return _sync_redis_client


async def close_redis() -> None:
    """Redis bağlantısını kapat."""
    global _redis_client, _sync_redis_client, _checkpointer
    
    # Checkpointer'ı temizle
    _checkpointer = None
    
    # Sync Redis client'ı kapat
    if _sync_redis_client is not None:
        _sync_redis_client.close()
        _sync_redis_client = None
    
    # Async Redis client'ı kapat
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


def get_checkpointer_sync() -> Union[RedisSaver, MemorySaver]:
    """
    LangGraph checkpointer (sync version).
    
    Graph compile edilirken kullanılır.
    RedisSaver ile mesaj geçmişi Redis'te kalıcı olarak saklanır.
    
    Returns:
        RedisSaver veya MemorySaver instance'ı
    """
    global _checkpointer
    
    if _checkpointer is None:
        try:
            # Sync Redis client al
            redis_client = get_sync_redis_client()
            
            # RedisSaver oluştur
            _checkpointer = RedisSaver(redis_client)
            print("✅ RedisSaver initialized - Messages will be stored in Redis")
        except Exception as e:
            print(f"⚠️ RedisSaver failed, falling back to MemorySaver: {e}")
            _checkpointer = MemorySaver()
    
    return _checkpointer
