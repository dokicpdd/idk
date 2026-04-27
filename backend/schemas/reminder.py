"""
Reminder Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from datetime import datetime


class ReminderCreate(BaseModel):
    """Payload to schedule a reminder for a task."""

    task_id: int
    remind_at: datetime


class ReminderRead(ReminderCreate):
    """Reminder representation returned by the API."""

    id: int
    sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}
