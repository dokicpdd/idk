"""
models/reminder.py

Reminder ORM model.
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, func, ForeignKey
from . import Base


class Reminder(Base):
    """Database table: reminders

    Stores scheduled reminders associated with a Task.
    """

    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
