"""
core/config.py

Application configuration settings.
Uses environment variables with sensible defaults.
"""

import os
from pathlib import Path


class Settings:
    """Application settings."""

    # Base directory
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tasks.db")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_to_a_secure_random_value")
    SESSION_MAX_AGE = 60 * 60 * 24  # 1 day

    # Application
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    APP_NAME = os.getenv("APP_NAME", "To-Do List App")


settings = Settings()
