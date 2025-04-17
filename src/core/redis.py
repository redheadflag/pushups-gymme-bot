from redis.asyncio import Redis

from core.config import redis_settings


redis = Redis(host=redis_settings.HOST, db=redis_settings.DB, port=redis_settings.PORT)
