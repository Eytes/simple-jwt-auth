from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Схема ответа с токенами."""

    access_token: str
    refresh_token: str


class TokenRequest(BaseModel):
    """Схема запроса с токеном"""

    token: str


class RefreshTokenRequest(BaseModel):
    """Схема запроса с refresh-токеном"""

    refresh_token: str
