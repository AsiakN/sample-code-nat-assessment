from aioredis import Redis
from pydantic import json

DEFAULT_KEY_PREFIX = 'is-bitcoin-lit'


def prefixed_key(f):
    """
    A method decorator that prefixes return values.

    Prefixes any string that the decorated method `f` returns with the value of
    the `prefix` attribute on the owner object `self`.
    """

    def prefixed_method(*args, **kwargs):
        self = args[0]
        key = f(*args, **kwargs)
        return f'{self.prefix}:{key}'

    return prefixed_method


class Keys:
    """Methods to generate key names for Redis data structures."""

    def __init__(self, prefix: str = DEFAULT_KEY_PREFIX):
        self.prefix = prefix

    @prefixed_key
    def timeseries_sentiment_key(self) -> str:
        """A time series containing 30-second snapshots of BTC sentiment."""
        return f'sentiment:mean:30s'

    @prefixed_key
    def timeseries_price_key(self) -> str:
        """A time series containing 30-second snapshots of BTC price."""
        return f'price:mean:30s'

    @prefixed_key
    def cache_key(self) -> str:
        return f'cache'


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.TWO_MINUTES = 2

    async def get_cache(self, keys: Keys):
        current_hour_cache_key = keys.cache_key()
        current_hour_stats = await self.redis.get(current_hour_cache_key)

        if current_hour_stats:
            return json.loads(current_hour_stats, object_hook=datetime_parser)

    async def set_cache(self, data, keys: Keys):
        def serialize_dates(v):
            return v.isoformat() if isinstance(v, datetime) else v

        await self.redis.set(
            keys.cache_key(),
            json.dumps(data, default=serialize_dates),
            ex=self.TWO_MINUTES,
        )
