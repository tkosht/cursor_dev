"""
Unit tests for task management skills.
Following TDD approach - tests written first.
"""

from unittest.mock import Mock

import pytest

from app.a2a_mvp.skills.task_skills import TaskSkill


class TestTaskSkills:
    """Test cases for task management skills."""

    @pytest.fixture
    def task_skill(self):
        """Create a TaskSkill instance for testing."""
        from app.a2a_mvp.skills.task_skills import TaskSkill
        from app.a2a_mvp.storage.memory import InMemoryStorage

        storage = InMemoryStorage()
        return TaskSkill(storage=storage)

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage for testing."""
        return Mock()

    def test_create_task_skill(self, task_skill):
        """Test creating a task through skill."""
        # Create task with minimal data
        result = task_skill.create_task({"title": "New Task"})

        assert result["success"] is True
        assert "task" in result
        assert result["task"]["title"] == "New Task"
        assert result["task"]["completed"] is False
        assert "id" in result["task"]
        assert "created_at" in result["task"]

    def test_create_task_with_description(self, task_skill):
        """Test creating a task with description."""
        result = task_skill.create_task(
            {
                "title": "Task with description",
                "description": "This is a detailed description",
            }
        )

        assert result["success"] is True
        assert (
            result["task"]["description"] == "This is a detailed description"
        )

    def test_create_task_missing_title(self, task_skill):
        """Test creating a task without title."""
        result = task_skill.create_task({})

        assert result["success"] is False
        assert "error" in result
        assert "title" in result["error"].lower()

    def test_get_task_skill(self, task_skill):
        """Test getting a task by ID."""
        # First create a task
        create_result = task_skill.create_task({"title": "Get me"})
        task_id = create_result["task"]["id"]

        # Get the task
        result = task_skill.get_task(task_id)

        assert result["success"] is True
        assert result["task"]["id"] == task_id
        assert result["task"]["title"] == "Get me"

    def test_get_nonexistent_task(self, task_skill):
        """Test getting a non-existent task."""
        result = task_skill.get_task("nonexistent-id")

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_list_tasks_empty(self, task_skill):
        """Test listing tasks when empty."""
        result = task_skill.list_tasks()

        assert result["success"] is True
        assert result["tasks"] == []
        assert result["count"] == 0

    def test_list_tasks_with_items(self, task_skill):
        """Test listing tasks with items."""
        # Create multiple tasks
        task_skill.create_task({"title": "Task 1"})
        task_skill.create_task({"title": "Task 2"})
        task_skill.create_task({"title": "Task 3"})

        result = task_skill.list_tasks()

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["tasks"]) == 3

        titles = [t["title"] for t in result["tasks"]]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_update_task_title(self, task_skill):
        """Test updating task title."""
        # Create a task
        create_result = task_skill.create_task({"title": "Original"})
        task_id = create_result["task"]["id"]

        # Update title
        result = task_skill.update_task(task_id, {"title": "Updated"})

        assert result["success"] is True
        assert result["task"]["title"] == "Updated"
        assert result["task"]["updated_at"] is not None

    def test_update_task_completion(self, task_skill):
        """Test updating task completion status."""
        # Create a task
        create_result = task_skill.create_task({"title": "Complete me"})
        task_id = create_result["task"]["id"]

        # Mark as complete
        result = task_skill.update_task(task_id, {"completed": True})

        assert result["success"] is True
        assert result["task"]["completed"] is True

    def test_update_nonexistent_task(self, task_skill):
        """Test updating a non-existent task."""
        result = task_skill.update_task("nonexistent-id", {"title": "New"})

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_delete_task(self, task_skill):
        """Test deleting a task."""
        # Create a task
        create_result = task_skill.create_task({"title": "Delete me"})
        task_id = create_result["task"]["id"]

        # Delete the task
        result = task_skill.delete_task(task_id)

        assert result["success"] is True
        assert result["message"] == f"Task {task_id} deleted successfully"

        # Verify it's gone
        get_result = task_skill.get_task(task_id)
        assert get_result["success"] is False

    def test_delete_nonexistent_task(self, task_skill):
        """Test deleting a non-existent task."""
        result = task_skill.delete_task("nonexistent-id")

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_toggle_task_completion(self, task_skill):
        """Test toggling task completion status."""
        # Create a task
        create_result = task_skill.create_task({"title": "Toggle me"})
        task_id = create_result["task"]["id"]

        # Toggle to complete
        result1 = task_skill.toggle_completion(task_id)
        assert result1["success"] is True
        assert result1["task"]["completed"] is True

        # Toggle back to incomplete
        result2 = task_skill.toggle_completion(task_id)
        assert result2["success"] is True
        assert result2["task"]["completed"] is False

    def test_clear_all_tasks(self, task_skill):
        """Test clearing all tasks."""
        # Create multiple tasks
        task_skill.create_task({"title": "Task 1"})
        task_skill.create_task({"title": "Task 2"})
        task_skill.create_task({"title": "Task 3"})

        # Clear all
        result = task_skill.clear_all_tasks()

        assert result["success"] is True
        assert result["message"] == "All tasks cleared successfully"

        # Verify all cleared
        list_result = task_skill.list_tasks()
        assert list_result["count"] == 0

    def test_execute_create_action(self, mock_storage):
        """Test execute method with create action."""
        skill = TaskSkill(mock_storage)
        mock_task = Mock()
        mock_task.to_dict.return_value = {"id": "1", "title": "New Task"}
        mock_storage.create_task.return_value = mock_task

        result = skill.execute(action="create", data={"title": "New Task"})

        assert result["success"] is True
        assert result["task"]["title"] == "New Task"

    def test_execute_get_action(self, mock_storage):
        """Test execute method with get action."""
        skill = TaskSkill(mock_storage)
        mock_task = Mock()
        mock_task.to_dict.return_value = {"id": "1", "title": "Test"}
        mock_storage.get_task.return_value = mock_task

        result = skill.execute(action="get", task_id="1")

        assert result["success"] is True
        assert result["task"]["id"] == "1"

    def test_execute_list_action(self, mock_storage):
        """Test execute method with list action."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_all_tasks.return_value = []

        result = skill.execute(action="list")

        assert result["success"] is True
        assert result["tasks"] == []

    def test_execute_update_action(self, mock_storage):
        """Test execute method with update action."""
        skill = TaskSkill(mock_storage)
        mock_task = Mock()
        mock_task.to_dict.return_value = {"id": "1", "title": "Updated"}
        mock_storage.update_task.return_value = mock_task

        result = skill.execute(
            action="update", task_id="1", data={"title": "Updated"}
        )

        assert result["success"] is True
        assert result["task"]["title"] == "Updated"

    def test_execute_delete_action(self, mock_storage):
        """Test execute method with delete action."""
        skill = TaskSkill(mock_storage)

        result = skill.execute(action="delete", task_id="1")

        assert result["success"] is True
        mock_storage.delete_task.assert_called_once_with("1")

    def test_execute_toggle_action(self, mock_storage):
        """Test execute method with toggle action."""
        skill = TaskSkill(mock_storage)
        mock_task = Mock()
        mock_task.completed = False
        mock_task.to_dict.return_value = {"id": "1", "completed": True}
        mock_storage.get_task.return_value = mock_task
        mock_storage.update_task.return_value = mock_task

        result = skill.execute(action="toggle", task_id="1")

        assert result["success"] is True

    def test_execute_clear_action(self, mock_storage):
        """Test execute method with clear action."""
        skill = TaskSkill(mock_storage)

        result = skill.execute(action="clear")

        assert result["success"] is True
        mock_storage.clear_all.assert_called_once()

    def test_execute_unknown_action(self, mock_storage):
        """Test execute method with unknown action."""
        skill = TaskSkill(mock_storage)

        result = skill.execute(action="unknown")

        assert result["success"] is False
        assert "Unknown action" in result["error"]

    def test_execute_default_action(self, mock_storage):
        """Test execute method with no action (defaults to list)."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_all_tasks.return_value = []

        result = skill.execute()

        assert result["success"] is True
        assert "tasks" in result

    def test_create_task_exception_handling(self, mock_storage):
        """Test create_task handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.create_task.side_effect = Exception("Storage error")

        result = skill.create_task({"title": "Test"})

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_get_task_exception_handling(self, mock_storage):
        """Test get_task handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_task.side_effect = Exception("Storage error")

        result = skill.get_task("1")

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_list_tasks_exception_handling(self, mock_storage):
        """Test list_tasks handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_all_tasks.side_effect = Exception("Storage error")

        result = skill.list_tasks()

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_update_task_exception_handling(self, mock_storage):
        """Test update_task handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_task.side_effect = Exception("Storage error")

        result = skill.update_task("1", {"title": "New"})

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_delete_task_exception_handling(self, mock_storage):
        """Test delete_task handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.delete_task.side_effect = Exception("Storage error")

        result = skill.delete_task("1")

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_toggle_completion_exception_handling(self, mock_storage):
        """Test toggle_completion handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.get_task.side_effect = Exception("Storage error")

        result = skill.toggle_completion("1")

        assert result["success"] is False
        assert "Storage error" in result["error"]

    def test_clear_all_tasks_exception_handling(self, mock_storage):
        """Test clear_all_tasks handles exceptions."""
        skill = TaskSkill(mock_storage)
        mock_storage.clear_all.side_effect = Exception("Storage error")

        result = skill.clear_all_tasks()

        assert result["success"] is False
        assert "Storage error" in result["error"]
