from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError, ExpiredSignatureError

from exceptions import (
    InvalidTokenHTTPException,
    ExpiredTokenHTTPException,
    TokenWrongTypeHTTPException,
)
from settings import settings
from redis_client import redis_client


def create_jwt_token(expires_delta: timedelta) -> str:
    """Создать JWT-токен с указанным временем жизни."""
    payload = {
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(
        payload, settings.PRIVATE_KEY_PATH.read_text(), algorithm=settings.ALGORITHM
    )


def verify_jwt_token(token: str) -> dict:
    """Проверить JWT-токен и вернуть его payload."""
    try:
        return jwt.decode(
            token,
            settings.PUBLIC_KEY_PATH.read_text(),
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise ExpiredTokenHTTPException
    except JWTError:
        raise InvalidTokenHTTPException


async def rotate_tokens_by_refresh_token(refresh_token: str) -> dict:
    """Обновляет Refresh токен и выдает новый Access и Refresh токен."""
    payload = verify_jwt_token(refresh_token)

    # Проверяем, что переданный токен действительно является refresh-токеном
    token_lifetime = payload.get("exp") - payload.get("iat")
    expected_lifetime = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

    if token_lifetime < expected_lifetime - 60:  # Допускаем небольшую погрешность
        raise TokenWrongTypeHTTPException

    # Если Access-токен был отозван, следовательно, и refresh-токен должен быть отозван
    access_token = await redis_client.get_value_by_token(refresh_token)
    if access_token is None:
        await redis_client.revoke_token(refresh_token)
        raise InvalidTokenHTTPException

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
        "user_id",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    await redis_client.set_token(
        new_refresh_token,
        new_access_token,
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}
