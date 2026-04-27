"""
core/security.py

Security utilities for password hashing and session tokens.
Uses passlib for password hashing and itsdangerous for tokens.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from passlib.context import CryptContext

from backend.core.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Session token signer
SIGNER = TimestampSigner(settings.SECRET_KEY)
SESSION_MAX_AGE = settings.SESSION_MAX_AGE


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain, hashed)


def create_session_token(username: str) -> str:
    """Create a signed session token for the user."""
    return SIGNER.sign(username.encode()).decode()


def verify_session_token(token: str) -> str:
    """Verify a session token and return the username.
    
    Raises:
        HTTPException: If token is expired or invalid.
    """
    try:
        val = SIGNER.unsign(token, max_age=SESSION_MAX_AGE)
        return val.decode()
    except SignatureExpired:
        raise HTTPException(status_code=401, detail="Session expired")
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid session token")
