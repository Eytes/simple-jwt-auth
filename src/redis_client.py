import redis.asyncio as redis
from settings import settings


class RedisClient:
    """Асинхронный клиент Redis для хранения и проверки токенов."""

    def __init__(self) -> None:
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def set_token(self, token: str, value: str, ttl: int) -> None:
        """Сохранить токен в Redis с временем жизни (TTL)."""
        await self.client.setex(token, ttl, value)

    async def get_value_by_token(self, token: str) -> str | None:
        """Получить user_id по токену, если он есть в Redis."""
        return await self.client.get(token)

    async def revoke_token(self, token: str) -> None:
        """Удалить токен из Redis (отзыв токена)."""
        await self.client.delete(token)


redis_client = RedisClient()
