from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError, ExpiredSignatureError

from exceptions import (
    InvalidTokenHTTPException,
    ExpiredTokenHTTPException,
    TokenWrongTypeHTTPException,
)
from settings import settings
from redis_client import redis_client


async def is_revoked(token: str) -> bool:
    """Проверяется был ли отозван токен. Если токена нет, токен был отозван"""
    value = await redis_client.get_value_by_token(token)
    return value is None


async def verify_jwt_token(token: str) -> dict:
    """Проверить JWT-токен и вернуть его payload."""
    try:
        if await is_revoked(token):
            raise ExpiredSignatureError
        return jwt.decode(
            token,
            settings.PUBLIC_KEY_PATH.read_text(),
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise ExpiredTokenHTTPException
    except JWTError:
        raise InvalidTokenHTTPException


async def is_refresh_token(token: str) -> bool:
    """Проверяем, что токен является refresh-токеном"""
    payload = await verify_jwt_token(token)
    token_lifetime = payload.get("exp") - payload.get("iat")
    expected_lifetime = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    return token_lifetime >= expected_lifetime - 60  # Допускаем небольшую погрешность


def create_jwt_token(expires_delta: timedelta) -> str:
    """Создать JWT-токен с указанным временем жизни."""
    now = datetime.now(UTC)
    payload = {
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(
        payload,
        settings.PRIVATE_KEY_PATH.read_text(),
        algorithm=settings.ALGORITHM,
    )


async def rotate_tokens_by_refresh_token(refresh_token: str) -> dict:
    """Обновляет Refresh токен и выдает новый Access и Refresh токен."""

    # Проверяем, что переданный токен действительно является refresh-токеном
    if not await is_refresh_token(refresh_token):
        raise TokenWrongTypeHTTPException

    access_token = await redis_client.get_value_by_token(refresh_token)

    await redis_client.revoke_token(access_token)
    await redis_client.revoke_token(refresh_token)

    new_access_token = create_jwt_token(
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_jwt_token(
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    await redis_client.set_token(
        new_access_token,
        "user_id",  # TODO: сделать привязку к данным пользователя или к сессии
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    await redis_client.set_token(
        new_refresh_token,
        new_access_token,
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}
