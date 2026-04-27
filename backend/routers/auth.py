"""routers/auth.py

Authentication endpoints (minimal):
- POST /auth/register : create a new user
- POST /auth/login    : login and set a session cookie
- POST /auth/logout   : clear session cookie
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import timedelta
from sqlalchemy import select

from backend.models import User
from backend.schemas.user import UserCreate, UserRead
from backend.core.database import get_session
from backend.core.security import hash_password, verify_password, create_session_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user.

    Expects JSON { username, password } and returns the created user (no password).
    """
    result = await session.execute(select(User).where(User.username == user_in.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/login")
async def login(response: Response, user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Authenticate user and set a short-lived session cookie.

    Body: { username, password }
    On success: cookie named 'token' is set (HttpOnly).
    """
    result = await session.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session_token(user.username)
    response.set_cookie(key="token", value=token, httponly=True, path="/", samesite="lax")
    return {"msg": "ok", "username": user.username}

@router.post("/logout")
async def logout(response: Response):
    """Log the user out by deleting the session cookie."""
    response.delete_cookie("token")
    return {"msg": "Logged out"}
