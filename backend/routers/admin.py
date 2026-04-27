"""
Admin router for backend management.

Provides endpoints for administrators to view system statistics,
manage users, and monitor tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from backend.core.database import get_session
from backend.models import User, Task
from backend.utils.auth import get_current_admin
from backend.schemas.user import UserRead
from backend.schemas.task import TaskRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    """Get system statistics."""
    # Count users
    users_result = await session.execute(select(func.count(User.id)))
    total_users = users_result.scalar()
    
    # Count tasks
    tasks_result = await session.execute(select(func.count(Task.id)))
    total_tasks = tasks_result.scalar()
    
    # Count completed tasks
    completed_result = await session.execute(
        select(func.count(Task.id)).where(Task.completed == True)
    )
    completed_tasks = completed_result.scalar()
    
    # Recent users (last 5)
    recent_users_result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(5)
    )
    recent_users = recent_users_result.scalars().all()
    
    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "recent_users": [
            {"id": u.id, "username": u.username, "created_at": u.created_at.isoformat()}
            for u in recent_users
        ]
    }


@router.get("/users", response_model=List[UserRead])
async def list_all_users(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    """List all users (admin only)."""
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}/tasks", response_model=List[TaskRead])
async def get_user_tasks(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    """Get tasks for a specific user (admin only)."""
    result = await session.execute(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin)
):
    """Delete a user and all their tasks (admin only)."""
    # Prevent admin from deleting themselves
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await session.delete(user)
    await session.commit()
    
    return {"success": True, "message": f"User {user.username} deleted"}
