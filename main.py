#!/usr/bin/env python3
"""
To-Do List Application Entry Point

Run with: python main.py
"""

from backend.backend import app
import uvicorn
from backend.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "backend.backend:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
