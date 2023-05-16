from aioredis import from_url, Redis
from typing import AsyncIterator
import logging

from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, host: str, password: str):
        self.host = host
        self.password = password

    @asynccontextmanager
    async def redis_session(self) -> AsyncIterator:
        session = from_url(f"redis://{self.host}", password=self.password, encoding="utf-8", decode_responses=True)
        try:
            yield session
        except Exception:
            logger.exception('Redis Session rollback because of exception')
            raise
        finally:
            session.close()
            await session.wait_closed()
