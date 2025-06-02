"""
Unit tests for the FastAPI server application.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.a2a_mvp.core.types import TaskResponse
from app.a2a_mvp.server.app import app


class TestServerApp:
    """Test FastAPI server endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        with patch("app.a2a_mvp.server.app.task_agent") as mock:
            yield mock

    def test_root_endpoint(self, client):
        """Test root endpoint returns agent card."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Task Manager Agent"
        assert "skills" in data
        assert len(data["skills"]) > 0
        assert "capabilities" in data

    def test_task_endpoint_create(self, client, mock_agent):
        """Test task creation through task endpoint."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True,
            data={"task": {"id": "test-id", "title": "Test Task"}},
        )

        response = client.post(
            "/task",
            json={
                "action": "create",
                "data": {
                    "title": "Test Task",
                    "description": "Test Description",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task" in data["data"]

    def test_task_endpoint_list(self, client, mock_agent):
        """Test listing tasks."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True, data={"tasks": []}
        )

        response = client.post("/task", json={"action": "list"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tasks" in data["data"]

    def test_task_endpoint_get(self, client, mock_agent):
        """Test getting a specific task."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True,
            data={"task": {"id": "test-id", "title": "Test Task"}},
        )

        response = client.post(
            "/task", json={"action": "get", "task_id": "test-id"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["task"]["id"] == "test-id"

    def test_task_endpoint_update(self, client, mock_agent):
        """Test updating a task."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True,
            data={"task": {"id": "test-id", "title": "Updated Task"}},
        )

        response = client.post(
            "/task",
            json={
                "action": "update",
                "task_id": "test-id",
                "data": {"title": "Updated Task"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_task_endpoint_delete(self, client, mock_agent):
        """Test deleting a task."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True, data={}
        )

        response = client.post(
            "/task", json={"action": "delete", "task_id": "test-id"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_task_endpoint_error(self, client, mock_agent):
        """Test error handling in task endpoint."""
        mock_agent.process_request.return_value = TaskResponse(
            success=False, error="Task not found"
        )

        response = client.post(
            "/task", json={"action": "get", "task_id": "non-existent"}
        )

        # The server currently returns 500 for all errors
        assert response.status_code == 500
        assert "Internal error" in response.json()["detail"]

    def test_task_endpoint_server_error(self, client, mock_agent):
        """Test server error handling."""
        mock_agent.process_request.side_effect = Exception("Server error")

        response = client.post("/task", json={"action": "list"})

        assert response.status_code == 500
        assert "Internal error" in response.json()["detail"]

    def test_a2a_message_endpoint_success(self, client, mock_agent):
        """Test A2A message handling."""
        mock_agent.handle_a2a_message.return_value = {
            "success": True,
            "message": "Request processed",
            "data": {"result": "success"},
        }

        a2a_message = {
            "agent": {"name": "TestAgent"},
            "skill": "task_management",
            "request": {"action": "list", "parameters": {}},
        }

        response = client.post("/a2a/message", json=a2a_message)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_a2a_message_endpoint_error(self, client, mock_agent):
        """Test A2A message error handling."""
        mock_agent.handle_a2a_message.return_value = {
            "success": False,
            "error": "Invalid message format",
        }

        response = client.post("/a2a/message", json={"invalid": "format"})
        # A2A endpoint returns 200 with error in response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_task_endpoint_toggle_completion(self, client, mock_agent):
        """Test toggling task completion."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True, data={"task": {"id": "test-id", "completed": True}}
        )

        response = client.post(
            "/task", json={"action": "toggle", "task_id": "test-id"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["task"]["completed"] is True

    def test_task_endpoint_clear_all(self, client, mock_agent):
        """Test clearing all tasks."""
        mock_agent.process_request.return_value = TaskResponse(
            success=True, data={}
        )

        response = client.post("/task", json={"action": "clear"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_agent_card_structure(self, client):
        """Test agent card has correct structure."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "name" in data
        assert "description" in data
        assert "version" in data
        assert "capabilities" in data
        assert "skills" in data

        # Check capabilities structure
        caps = data["capabilities"]
        assert "streaming" in caps
        assert "push_notifications" in caps

        # Check skills structure
        assert len(data["skills"]) > 0
        skill = data["skills"][0]
        assert "id" in skill
        assert "name" in skill
        assert "description" in skill
        assert "tags" in skill
        assert "examples" in skill
