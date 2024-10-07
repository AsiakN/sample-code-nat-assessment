from _decimal import Decimal
from aioredis import Redis
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.CACHE_EXPIRE_IN = 300

    async def get_cache(self, key: str):
        """Retrieve cached data for the given user_id."""
        cached_data = await self.redis.get(f"{key}")
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_cache(self, data, key: str):
        await self.redis.set(
            key,
            json.dumps(data, cls=DecimalEncoder),
            ex=self.CACHE_EXPIRE_IN,
        )
