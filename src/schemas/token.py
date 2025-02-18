from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Схема ответа с токенами."""

    access_token: str
    refresh_token: str
