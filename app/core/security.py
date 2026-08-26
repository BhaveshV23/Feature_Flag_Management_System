from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ValidationError

from app.services.auth_service import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    user_id: int
    username: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise unauthorized

    try:
        return AuthenticatedUser(
            user_id=payload["user_id"],
            username=payload["sub"],
        )
    except (KeyError, TypeError, ValidationError):
        raise unauthorized from None
