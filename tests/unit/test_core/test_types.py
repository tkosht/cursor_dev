"""
Unit tests for A2A MVP core types.
Following TDD approach - tests written first.
"""
import pytest
from datetime import datetime
from typing import Dict, Any
import uuid


class TestTaskTypes:
    """Test cases for Task-related types."""
    
    def test_task_creation_with_required_fields(self):
        """Test creating a Task with required fields only."""
        from app.a2a_mvp.core.types import Task
        
        task = Task(
            id=str(uuid.uuid4()),
            title="Buy groceries",
            created_at=datetime.now()
        )
        
        assert task.id is not None
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert task.updated_at is None
    
    def test_task_creation_with_all_fields(self):
        """Test creating a Task with all fields."""
        from app.a2a_mvp.core.types import Task
        
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            id=task_id,
            title="Complete project",
            description="Finish the A2A implementation",
            completed=True,
            created_at=now,
            updated_at=now
        )
        
        assert task.id == task_id
        assert task.title == "Complete project"
        assert task.description == "Finish the A2A implementation"
        assert task.completed is True
        assert task.created_at == now
        assert task.updated_at == now
    
    def test_task_to_dict(self):
        """Test converting Task to dictionary."""
        from app.a2a_mvp.core.types import Task
        
        task = Task(
            id="task-123",
            title="Test task",
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        task_dict = task.to_dict()
        
        assert task_dict["id"] == "task-123"
        assert task_dict["title"] == "Test task"
        assert task_dict["description"] is None
        assert task_dict["completed"] is False
        assert task_dict["created_at"] == "2024-01-01T12:00:00"
        assert task_dict["updated_at"] is None
    
    def test_task_from_dict(self):
        """Test creating Task from dictionary."""
        from app.a2a_mvp.core.types import Task
        
        task_dict = {
            "id": "task-456",
            "title": "From dict task",
            "description": "Created from dictionary",
            "completed": True,
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-02T12:00:00"
        }
        
        task = Task.from_dict(task_dict)
        
        assert task.id == "task-456"
        assert task.title == "From dict task"
        assert task.description == "Created from dictionary"
        assert task.completed is True
        assert task.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert task.updated_at == datetime(2024, 1, 2, 12, 0, 0)


class TestA2AMessageTypes:
    """Test cases for A2A message types."""
    
    def test_task_request_creation(self):
        """Test creating a TaskRequest."""
        from app.a2a_mvp.core.types import TaskRequest
        
        request = TaskRequest(
            action="create",
            data={"title": "New task"}
        )
        
        assert request.action == "create"
        assert request.data == {"title": "New task"}
        assert request.task_id is None
    
    def test_task_request_with_task_id(self):
        """Test creating a TaskRequest with task_id."""
        from app.a2a_mvp.core.types import TaskRequest
        
        request = TaskRequest(
            action="update",
            task_id="task-123",
            data={"completed": True}
        )
        
        assert request.action == "update"
        assert request.task_id == "task-123"
        assert request.data == {"completed": True}
    
    def test_task_response_success(self):
        """Test creating a successful TaskResponse."""
        from app.a2a_mvp.core.types import TaskResponse
        
        response = TaskResponse(
            success=True,
            data={"id": "task-123", "title": "Created task"}
        )
        
        assert response.success is True
        assert response.data == {"id": "task-123", "title": "Created task"}
        assert response.error is None
    
    def test_task_response_error(self):
        """Test creating an error TaskResponse."""
        from app.a2a_mvp.core.types import TaskResponse
        
        response = TaskResponse(
            success=False,
            error="Task not found"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error == "Task not found"
    
    def test_a2a_skill_definition(self):
        """Test A2ASkill type definition."""
        from app.a2a_mvp.core.types import A2ASkill
        
        skill = A2ASkill(
            id="task_management",
            name="Task Management",
            description="Manage TODO tasks",
            tags=["productivity", "tasks"],
            examples=["Create a new task", "Mark task as done"]
        )
        
        assert skill.id == "task_management"
        assert skill.name == "Task Management"
        assert skill.description == "Manage TODO tasks"
        assert skill.tags == ["productivity", "tasks"]
        assert skill.examples == ["Create a new task", "Mark task as done"]
    
    def test_a2a_agent_card(self):
        """Test A2AAgentCard type definition."""
        from app.a2a_mvp.core.types import A2AAgentCard, A2ACapabilities, A2ASkill
        
        capabilities = A2ACapabilities(
            streaming=False,
            push_notifications=False
        )
        
        skill = A2ASkill(
            id="task_management",
            name="Task Management",
            description="Manage TODO tasks",
            tags=["productivity"],
            examples=[]
        )
        
        card = A2AAgentCard(
            name="Task Manager Agent",
            description="An agent for managing TODO tasks",
            version="1.0.0",
            url="http://localhost:8000",
            capabilities=capabilities,
            skills=[skill]
        )
        
        assert card.name == "Task Manager Agent"
        assert card.description == "An agent for managing TODO tasks"
        assert card.version == "1.0.0"
        assert card.url == "http://localhost:8000"
        assert card.capabilities.streaming is False
        assert card.capabilities.push_notifications is False
        assert len(card.skills) == 1
        assert card.skills[0].id == "task_management"