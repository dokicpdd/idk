"""
Test suite for the To-Do List API.

Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from backend.backend import app

client = TestClient(app)


class TestPages:
    """Tests for HTML page routes."""

    def test_root_redirect(self):
        """Test that root redirects to index."""
        res = client.get("/", follow_redirects=False)
        assert res.status_code in (307, 302)
        assert "/index" in res.headers.get("location", "")

    def test_index_page_redirects_to_login_when_unauthenticated(self):
        """Test index page redirects to login when not authenticated."""
        res = client.get("/index", follow_redirects=False)
        assert res.status_code in (307, 302)
        assert "/login" in res.headers.get("location", "")

    def test_login_page(self):
        """Test login page loads."""
        res = client.get("/login")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")

    def test_register_page(self):
        """Test register page loads."""
        res = client.get("/register")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")

    def test_task_page_redirects_to_login_when_unauthenticated(self):
        """Test task page redirects to login when not authenticated."""
        res = client.get("/task", follow_redirects=False)
        assert res.status_code in (307, 302)
        assert "/login" in res.headers.get("location", "")

    def test_index_page_redirects_to_login_when_unauthenticated(self):
        """Test index page redirects to login when not authenticated."""
        res = client.get("/index", follow_redirects=False)
        assert res.status_code in (307, 302)
        assert "/login" in res.headers.get("location", "")

    def test_login_page_redirects_to_index_when_authenticated(self):
        """Test login page redirects to index when already authenticated."""
        import uuid
        username = f"pageuser_{uuid.uuid4().hex[:8]}"
        # Register and login
        client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        login_res = client.post("/auth/login", json={
            "username": username,
            "password": "testpass123"
        })
        # Create new client with cookie
        auth_client = TestClient(app)
        auth_client.cookies.set("token", login_res.cookies["token"])
        # Try to access login page
        res = auth_client.get("/login", follow_redirects=False)
        assert res.status_code in (307, 302)
        assert "/index" in res.headers.get("location", "")


class TestAuth:
    """Tests for authentication endpoints."""

    def test_register_user_success(self):
        """Test successful user registration."""
        import uuid
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        res = client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == username
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_username(self):
        """Test registration with duplicate username fails."""
        import uuid
        username = f"dupuser_{uuid.uuid4().hex[:8]}"
        # First registration
        client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        # Second registration with same username
        res = client.post("/auth/register", json={
            "username": username,
            "password": "differentpass"
        })
        assert res.status_code == 400
        assert "already taken" in res.json()["error"]["message"]

    def test_login_success(self):
        """Test successful login sets cookie."""
        import uuid
        username = f"loginuser_{uuid.uuid4().hex[:8]}"
        # Register first
        client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        # Login
        res = client.post("/auth/login", json={
            "username": username,
            "password": "testpass123"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["msg"] == "ok"
        assert data["username"] == username
        # Check cookie is set
        assert "token" in res.cookies

    def test_login_invalid_credentials(self):
        """Test login with wrong password fails."""
        import uuid
        username = f"baduser_{uuid.uuid4().hex[:8]}"
        # Register first
        client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
        # Login with wrong password
        res = client.post("/auth/login", json={
            "username": username,
            "password": "wrongpassword"
        })
        assert res.status_code == 401
        assert "Invalid" in res.json()["error"]["message"]

    def test_logout(self):
        """Test logout clears cookie."""
        res = client.post("/auth/logout")
        assert res.status_code == 200
        assert res.json()["msg"] == "Logged out"


class TestTasks:
    """Tests for task endpoints."""

    @pytest.fixture
    def auth_client(self):
        """Create an authenticated test client."""
        import uuid
        username = f"taskuser_{uuid.uuid4().hex[:8]}"
        password = "test123"
        
        # Register
        client.post("/auth/register", json={
            "username": username,
            "password": password
        })
        
        # Login to get cookie
        login_res = client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        
        # Create new client with cookie
        authenticated_client = TestClient(app)
        authenticated_client.cookies.set("token", login_res.cookies["token"])
        
        return authenticated_client

    def test_get_tasks_unauthenticated(self):
        """Test getting tasks without auth fails."""
        # Create fresh client without cookies
        unauth_client = TestClient(app)
        res = unauth_client.get("/api/tasks")
        assert res.status_code == 401

    def test_create_and_list_task(self, auth_client):
        """Test creating and listing tasks."""
        import uuid
        
        # Create task
        task_content = f"Test task {uuid.uuid4().hex[:8]}"
        create_res = auth_client.post("/api/tasks", json={
            "content": task_content,
            "completed": False
        })
        assert create_res.status_code == 201
        task = create_res.json()
        assert task["content"] == task_content
        assert task["completed"] == False
        assert "id" in task
        
        # List tasks
        list_res = auth_client.get("/api/tasks")
        assert list_res.status_code == 200
        tasks = list_res.json()
        assert isinstance(tasks, list)
        assert any(t["content"] == task_content for t in tasks)

    def test_update_task(self, auth_client):
        """Test updating a task."""
        import uuid
        
        # Create task
        create_res = auth_client.post("/api/tasks", json={
            "content": f"Original {uuid.uuid4().hex[:8]}",
            "completed": False
        })
        task_id = create_res.json()["id"]
        
        # Update task
        update_res = auth_client.put(f"/api/tasks/{task_id}", json={
            "content": "Updated content",
            "completed": True
        })
        assert update_res.status_code == 200
        updated = update_res.json()
        assert updated["content"] == "Updated content"
        assert updated["completed"] == True

    def test_delete_task(self, auth_client):
        """Test deleting a task."""
        import uuid
        
        # Create task
        create_res = auth_client.post("/api/tasks", json={
            "content": f"To delete {uuid.uuid4().hex[:8]}",
            "completed": False
        })
        task_id = create_res.json()["id"]
        
        # Delete task
        delete_res = auth_client.delete(f"/api/tasks/{task_id}")
        assert delete_res.status_code == 200
        assert delete_res.json()["success"] == True
        
        # Verify deletion
        list_res = auth_client.get("/api/tasks")
        tasks = list_res.json()
        assert not any(t["id"] == task_id for t in tasks)

    def test_update_nonexistent_task(self, auth_client):
        """Test updating a non-existent task returns 404."""
        res = auth_client.put("/api/tasks/99999", json={
            "content": "Nonexistent",
            "completed": True
        })
        assert res.status_code == 404

    def test_delete_nonexistent_task(self, auth_client):
        """Test deleting a non-existent task returns 404."""
        res = auth_client.delete("/api/tasks/99999")
        assert res.status_code == 404
