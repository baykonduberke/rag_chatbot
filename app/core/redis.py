"""
Redis Connection Manager

Redis bağlantısını ve LangGraph checkpointer'ını yönetir.
Mesaj geçmişi Redis'te saklanır (kalıcı).
"""

from typing import Optional, Union
import redis.asyncio as redis
from redis.exceptions import ConnectionError as RedisConnectionError
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings


# Redis client singleton
_redis_client: Optional[redis.Redis] = None

# Async Checkpointer singleton
_async_checkpointer: Optional[Union[any, MemorySaver]] = None


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


async def close_redis() -> None:
    """Redis bağlantısını kapat."""
    global _redis_client, _async_checkpointer
    
    _async_checkpointer = None
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def get_async_checkpointer() -> Union[any, MemorySaver]:
    """
    LangGraph async checkpointer.
    
    Returns:
        AsyncRedisSaver veya MemorySaver instance'ı
    """
    global _async_checkpointer
    
    if _async_checkpointer is None:
        try:
            from langgraph.checkpoint.redis.aio import AsyncRedisSaver
            
            # AsyncRedisSaver oluştur
            _async_checkpointer = AsyncRedisSaver(redis_url=settings.REDIS_URL)
            
            # Gerekli indeksleri oluştur
            await _async_checkpointer.asetup()
            print(f"✅ AsyncRedisSaver initialized - Redis URL: {settings.REDIS_URL}")
        except ImportError:
            print("❌ langgraph-checkpoint-redis not installed, using MemorySaver")
            _async_checkpointer = MemorySaver()
        except RedisConnectionError as e:
            print(f"❌ Redis connection failed: {e}")
            print("⚠️ Falling back to MemorySaver - Messages will be lost on restart!")
            _async_checkpointer = MemorySaver()
        except Exception as e:
            print(f"❌ AsyncRedisSaver initialization failed: {e}")
            print("⚠️ Falling back to MemorySaver - Messages will be lost on restart!")
            _async_checkpointer = MemorySaver()
    
    return _async_checkpointer


# def get_checkpointer_sync() -> MemorySaver:
#     """Sync checkpointer (sadece compile için)."""
#     return MemorySaver()
