from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False, index=True)
    tags = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Pydantic schemas for request/response validation
class TaskCreate(BaseModel):
    content: str
    tags: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False

class TaskRead(TaskCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

