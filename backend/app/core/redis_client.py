"""Redis client using fakeredis for zero-install local operation.
Swap fakeredis.FakeRedis for redis.asyncio.Redis for real Redis server.
"""
import asyncio
import json
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

# Use fakeredis — no installation required
# To use real Redis: pip install redis and change below to:
#   import redis.asyncio as redis_lib
#   _redis = redis_lib.from_url(REDIS_URL)
try:
    import fakeredis.aioredis as fakeredis_async
    _USING_FAKE = True
except ImportError:
    _USING_FAKE = False
    try:
        import redis.asyncio as redis_lib
    except ImportError:
        redis_lib = None

_redis_instance = None

async def get_redis():
    global _redis_instance
    if _redis_instance is not None:
        return _redis_instance
    if _USING_FAKE:
        _redis_instance = fakeredis_async.FakeRedis(decode_responses=True)
        logger.info('Redis: using fakeredis (in-process)')
    elif redis_lib:
        from backend.app.core.config import settings
        _redis_instance = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info('Redis: connected to real Redis server')
    else:
        raise RuntimeError('Neither fakeredis nor redis package installed')
    return _redis_instance

async def publish_alert(alert_data: dict):
    """Publish alert to Redis channel for WebSocket broadcast."""
    try:
        r = await get_redis()
        await r.publish('sentinel:alerts', json.dumps(alert_data))
    except Exception as e:
        logger.error(f'Redis publish error: {e}')

async def publish_anpr(anpr_data: dict):
    """Publish ANPR event to Redis channel."""
    try:
        r = await get_redis()
        await r.publish('sentinel:anpr', json.dumps(anpr_data))
    except Exception as e:
        logger.error(f'Redis ANPR publish error: {e}')

async def cache_set(key: str, value: Any, ttl: int = 60):
    try:
        r = await get_redis()
        await r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f'Redis cache_set error: {e}')

async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        val = await r.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.error(f'Redis cache_get error: {e}')
        return None