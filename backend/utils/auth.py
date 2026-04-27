"""
utils/auth.py

Authentication dependencies and utilities for FastAPI.
"""

from typing import Optional

from fastapi import HTTPException, Response, Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_session
from backend.models import User
from backend.core.security import verify_session_token


async def get_current_user(
    response: Response = None,
    token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_session)
):
    """Dependency to get the current authenticated user.
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = verify_session_token(token)
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_current_user_optional(token: Optional[str] = Cookie(None)) -> Optional[str]:
    """Get current username from cookie, return None if not authenticated.
    
    Used for HTML page routes to check authentication status without raising exceptions.
    """
    if not token:
        return None
    try:
        return verify_session_token(token)
    except HTTPException:
        return None


async def get_current_admin(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Dependency to ensure user is an admin.
    
    Raises:
        HTTPException: If user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
