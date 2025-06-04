"""
Unit tests for task management agent.
Following TDD approach - tests written first.
"""

import pytest


class TestTaskAgent:
    """Test cases for TaskAgent."""

    @pytest.fixture
    def task_agent(self):
        """Create a TaskAgent instance for testing."""
        from app.a2a.agents.task_agent import TaskAgent
        from app.a2a.storage.memory import InMemoryStorage

        storage = InMemoryStorage()
        return TaskAgent(storage=storage)

    def test_agent_card(self, task_agent):
        """Test agent card generation."""
        card = task_agent.get_agent_card()

        assert card.name == "Task Manager Agent"
        assert card.version == "1.0.0"
        assert "task" in card.description.lower()
        assert len(card.skills) > 0

        # Check for essential skills
        skill_ids = [skill.id for skill in card.skills]
        assert "create_task" in skill_ids
        assert "list_tasks" in skill_ids
        assert "update_task" in skill_ids
        assert "delete_task" in skill_ids

    def test_process_create_task_request(self, task_agent):
        """Test processing create task request."""
        from app.a2a.core.types import TaskRequest

        request = TaskRequest(
            action="create",
            data={"title": "Test Task", "description": "Test Description"},
        )

        response = task_agent.process_request(request)

        assert response.success is True
        assert "id" in response.data
        assert response.data["title"] == "Test Task"
        assert response.data["description"] == "Test Description"

    def test_process_list_tasks_request(self, task_agent):
        """Test processing list tasks request."""
        from app.a2a.core.types import TaskRequest

        # First create some tasks
        task_agent.process_request(
            TaskRequest(action="create", data={"title": "Task 1"})
        )
        task_agent.process_request(
            TaskRequest(action="create", data={"title": "Task 2"})
        )

        # List tasks
        request = TaskRequest(action="list")
        response = task_agent.process_request(request)

        assert response.success is True
        assert "tasks" in response.data
        assert "count" in response.data
        assert response.data["count"] == 2
        assert len(response.data["tasks"]) == 2

    def test_process_get_task_request(self, task_agent):
        """Test processing get task request."""
        from app.a2a.core.types import TaskRequest

        # Create a task
        create_response = task_agent.process_request(
            TaskRequest(action="create", data={"title": "Get Me"})
        )
        task_id = create_response.data["id"]

        # Get the task
        request = TaskRequest(action="get", task_id=task_id)
        response = task_agent.process_request(request)

        assert response.success is True
        assert response.data["id"] == task_id
        assert response.data["title"] == "Get Me"

    def test_process_update_task_request(self, task_agent):
        """Test processing update task request."""
        from app.a2a.core.types import TaskRequest

        # Create a task
        create_response = task_agent.process_request(
            TaskRequest(action="create", data={"title": "Original"})
        )
        task_id = create_response.data["id"]

        # Update the task
        request = TaskRequest(
            action="update",
            task_id=task_id,
            data={"title": "Updated", "completed": True},
        )
        response = task_agent.process_request(request)

        assert response.success is True
        assert response.data["title"] == "Updated"
        assert response.data["completed"] is True
        assert response.data["updated_at"] is not None

    def test_process_delete_task_request(self, task_agent):
        """Test processing delete task request."""
        from app.a2a.core.types import TaskRequest

        # Create a task
        create_response = task_agent.process_request(
            TaskRequest(action="create", data={"title": "Delete Me"})
        )
        task_id = create_response.data["id"]

        # Delete the task
        request = TaskRequest(action="delete", task_id=task_id)
        response = task_agent.process_request(request)

        assert response.success is True
        assert "message" in response.data

        # Verify deletion
        get_response = task_agent.process_request(
            TaskRequest(action="get", task_id=task_id)
        )
        assert get_response.success is False

    def test_process_toggle_completion_request(self, task_agent):
        """Test processing toggle completion request."""
        from app.a2a.core.types import TaskRequest

        # Create a task
        create_response = task_agent.process_request(
            TaskRequest(action="create", data={"title": "Toggle Me"})
        )
        task_id = create_response.data["id"]

        # Toggle completion
        request = TaskRequest(action="toggle", task_id=task_id)
        response = task_agent.process_request(request)

        assert response.success is True
        assert response.data["completed"] is True

        # Toggle again
        response2 = task_agent.process_request(request)
        assert response2.success is True
        assert response2.data["completed"] is False

    def test_process_clear_all_request(self, task_agent):
        """Test processing clear all request."""
        from app.a2a.core.types import TaskRequest

        # Create some tasks
        task_agent.process_request(
            TaskRequest(action="create", data={"title": "Task 1"})
        )
        task_agent.process_request(
            TaskRequest(action="create", data={"title": "Task 2"})
        )

        # Clear all
        request = TaskRequest(action="clear")
        response = task_agent.process_request(request)

        assert response.success is True

        # Verify all cleared
        list_response = task_agent.process_request(TaskRequest(action="list"))
        assert list_response.data["count"] == 0

    def test_process_invalid_action(self, task_agent):
        """Test processing invalid action."""
        from app.a2a.core.types import TaskRequest

        request = TaskRequest(action="invalid_action")
        response = task_agent.process_request(request)

        assert response.success is False
        assert response.error is not None
        assert "invalid" in response.error.lower()

    def test_process_create_without_title(self, task_agent):
        """Test creating task without title."""
        from app.a2a.core.types import TaskRequest

        request = TaskRequest(action="create", data={})
        response = task_agent.process_request(request)

        assert response.success is False
        assert "title" in response.error.lower()

    def test_handle_a2a_message(self, task_agent):
        """Test handling A2A protocol message."""
        # Simulate A2A message for creating a task
        message = {
            "type": "task_management",
            "action": "create",
            "data": {"title": "A2A Task"},
        }

        result = task_agent.handle_a2a_message(message)

        assert result["success"] is True
        assert result["data"]["title"] == "A2A Task"

    def test_handle_invalid_a2a_message(self, task_agent):
        """Test handling invalid A2A message."""
        # Message without required fields
        message = {"invalid": "message"}

        result = task_agent.handle_a2a_message(message)

        assert result["success"] is False
        assert "error" in result
