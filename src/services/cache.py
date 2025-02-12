import aioredis
from src.conf.config import settings

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
