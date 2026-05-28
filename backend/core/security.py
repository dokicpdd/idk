"""
core/security.py

Security utilities for password hashing and JWT tokens.
Uses passlib for password hashing and python-jose for JWTs.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_SECONDS


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str, expires_delta: Optional[int] = None) -> str:
    """Create a JWT access token for the given username.

    Args:
        username: the username to include in the token subject (sub)
        expires_delta: expiration in seconds (overrides default)

    Returns:
        encoded JWT as string
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=(expires_delta if expires_delta is not None else ACCESS_TOKEN_EXPIRE_SECONDS))
    to_encode = {"sub": username, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> str:
    """Verify a JWT and return the username (sub).

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
