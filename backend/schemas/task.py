"""
Task Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    """Payload used when creating or replacing a Task from the API."""

    content: str
    tags: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False


class TaskRead(TaskCreate):
    """Schema returned by the API for read operations (includes DB fields)."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # Pydantic v2: allow from_orm() with SQLAlchemy objects
