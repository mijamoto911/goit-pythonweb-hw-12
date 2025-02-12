import aioredis
import json
from fastapi import Depends
from typing import Optional
from src.conf.config import settings  # Налаштування конфігурації


class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def set(self, key: str, value: dict, expire: int = 3600):
        """Зберігає об'єкт у Redis на певний час"""
        await self.redis.setex(key, expire, json.dumps(value))

    async def get(self, key: str) -> Optional[dict]:
        """Отримує дані з Redis"""
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def delete(self, key: str):
        """Видаляє ключ із Redis"""
        await self.redis.delete(key)

    async def close(self):
        """Закриває підключення до Redis"""
        await self.redis.close()


redis_cache = RedisCache()
