"""
Pytest configuration and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.backend import app
from backend.models import Base

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_user():
    """Return test user credentials."""
    import uuid
    return {
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "testpassword123"
    }
