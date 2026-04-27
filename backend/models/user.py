"""
models/user.py

User ORM model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from . import Base


class User(Base):
    """Database table: users

    Fields:
    - id: primary key
    - username: unique login name
    - hashed_password: password hash (never store plain text)
    - is_admin: admin flag
    - created_at: timestamp
    - tasks: relationship back to Task (optional)
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    tasks = relationship("Task", back_populates="owner")
