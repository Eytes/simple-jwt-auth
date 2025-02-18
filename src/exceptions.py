from fastapi import HTTPException, status


class InvalidTokenHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )


class ExpiredTokenHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )


class TokenWrongTypeHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided token is not a refresh token",
        )
