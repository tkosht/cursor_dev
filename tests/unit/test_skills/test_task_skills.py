"""
Unit tests for task management skills.
Following TDD approach - tests written first.
"""
import pytest
from datetime import datetime
from typing import Dict, Any
import uuid


class TestTaskSkills:
    """Test cases for task management skills."""
    
    @pytest.fixture
    def task_skill(self):
        """Create a TaskSkill instance for testing."""
        from app.a2a_mvp.skills.task_skills import TaskSkill
        from app.a2a_mvp.storage.memory import InMemoryStorage
        
        storage = InMemoryStorage()
        return TaskSkill(storage=storage)
    
    def test_create_task_skill(self, task_skill):
        """Test creating a task through skill."""
        # Create task with minimal data
        result = task_skill.create_task({
            "title": "New Task"
        })
        
        assert result["success"] is True
        assert "task" in result
        assert result["task"]["title"] == "New Task"
        assert result["task"]["completed"] is False
        assert "id" in result["task"]
        assert "created_at" in result["task"]
    
    def test_create_task_with_description(self, task_skill):
        """Test creating a task with description."""
        result = task_skill.create_task({
            "title": "Task with description",
            "description": "This is a detailed description"
        })
        
        assert result["success"] is True
        assert result["task"]["description"] == "This is a detailed description"
    
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