"""
User Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    """Payload for registering / logging in a user (simple form).

    Note: `password` is plain-text here only during registration/login; the
    application must store a hashed password in the database.
    """

    username: str
    password: str


class UserRead(BaseModel):
    """Public representation of a user returned by the API (no password)."""

    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
