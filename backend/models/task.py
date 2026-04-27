"""
models/task.py

Task ORM model.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class Task(Base):
    """Database table: tasks

    Fields:
    - id: primary key
    - user_id: foreign key to users table
    - content: task text (required)
    - tags: optional comma-separated tags
    - priority: optional integer priority (e.g. 1-5)
    - due_date: optional due date/time
    - completed: boolean flag
    - created_at / updated_at: timestamps (DB default)
    """

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False, index=True)
    tags = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    owner = relationship("User", back_populates="tasks")
