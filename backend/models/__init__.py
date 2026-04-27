"""
db/__init__.py

SQLAlchemy ORM models (database tables).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models (SQLAlchemy 2.0 style)."""
    pass


from .task import Task
from .user import User
from .reminder import Reminder

__all__ = ["Base", "Task", "User", "Reminder"]
