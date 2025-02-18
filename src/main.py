from typing import Annotated

from fastapi import FastAPI, status
from datetime import timedelta

from fastapi.params import Depends

from schemas.token import TokenResponse
from utils.jwt_handler import (
    create_jwt_token,
    verify_jwt_token,
    rotate_tokens_by_refresh_token,
)
from redis_client import redis_client
from settings import settings

app = FastAPI(
    title="Simple JWT service",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.post(
    "/api/tokens",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_token() -> TokenResponse:
    """Создать access и refresh токены."""
    access_token = create_jwt_token(
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_jwt_token(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    await redis_client.set_token(
        access_token, "user_id", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    await redis_client.set_token(
        refresh_token, access_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.get(
    "/api/tokens/verify",
    status_code=status.HTTP_200_OK,
)
async def verify_tokens(payload: Annotated[dict, Depends(verify_jwt_token)]) -> dict:
    """Проверить токен и вернуть payload"""
    return payload


@app.post(
    "/api/tokens/rotate",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def rotate_tokens(refresh_token: str) -> TokenResponse:
    """Выпустить новые access и refresh токены, на основе уже существующего refresh token"""
    new_access_token, new_refresh_token = (
        await rotate_tokens_by_refresh_token(refresh_token)
    ).values()
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


# @app.delete(
#     "/api/tokens/revoke",
#     status_code=status.HTTP_200_OK,
# )
# async def revoke_token(token: str) -> dict:
#     """Отозвать токен."""
#     verify_jwt_token(token)
#     await redis_client.revoke_token(token)
#     return {"message": "Token revoked"}
