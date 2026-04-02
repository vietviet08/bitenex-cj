"""JWT authentication and RBAC utilities."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import Settings, get_settings


class Role(str, Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    ANALYST = "analyst"
    OPERATOR = "operator"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # user_id
    role: Role
    exp: datetime


security = HTTPBearer()


def create_access_token(
    user_id: str,
    role: Role,
    settings: Settings | None = None,
) -> str:
    """Create a JWT access token."""
    if settings is None:
        settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "role": role.value,
        "exp": expire,
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str, settings: Settings) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(
            sub=payload["sub"],
            role=Role(payload["role"]),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:
    """Dependency to get the current authenticated user."""
    return decode_token(credentials.credentials, settings)


def require_roles(*roles: Role):
    """Dependency factory to require specific roles."""

    async def check_role(
        current_user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not authorized. Required: {[r.value for r in roles]}",
            )
        return current_user

    return check_role


# Convenience dependencies
require_admin = require_roles(Role.ADMIN)
require_analyst = require_roles(Role.ADMIN, Role.ANALYST)
require_operator = require_roles(Role.ADMIN, Role.OPERATOR)
