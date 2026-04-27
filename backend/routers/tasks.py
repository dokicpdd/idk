from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, UTC

from backend.models import Task, User
from backend.schemas.task import TaskCreate, TaskRead
from backend.core.database import get_session
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all tasks for the current user."""
    stmt = select(Task).where(Task.user_id == current_user.id).order_by(Task.created_at)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return tasks

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new task for the current user."""
    # Check for duplicate content for this user
    stmt = select(Task).where(
        Task.user_id == current_user.id,
        Task.content == task_in.content
    )
    result = await session.execute(stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Task already exists")
    
    db_task = Task(
        user_id=current_user.id,
        content=task_in.content,
        tags=task_in.tags,
        priority=task_in.priority,
        due_date=task_in.due_date,
        completed=task_in.completed,
    )
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_in: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a task (only if owned by current user)."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.content = task_in.content
    db_task.tags = task_in.tags
    db_task.priority = task_in.priority
    db_task.due_date = task_in.due_date
    db_task.completed = task_in.completed
    db_task.updated_at = datetime.now(UTC)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(
    task_id: int,
    task_in: TaskRead,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Partially update a task (only if owned by current user)."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db_task.updated_at = datetime.now(UTC)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a task (only if owned by current user)."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await session.delete(db_task)
    await session.commit()
    return {"success": True}
