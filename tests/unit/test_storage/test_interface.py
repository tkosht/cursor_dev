"""
Unit tests for storage interface.
Following TDD approach - tests written first.
"""
import pytest
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime


class TestStorageInterface:
    """Test cases for storage interface definition."""
    
    def test_storage_interface_methods(self):
        """Test that StorageInterface defines all required methods."""
        from app.a2a_mvp.storage.interface import StorageInterface
        from app.a2a_mvp.core.types import Task
        
        # StorageInterface should be abstract
        assert issubclass(StorageInterface, ABC)
        
        # Check required abstract methods
        assert hasattr(StorageInterface, 'create_task')
        assert hasattr(StorageInterface, 'get_task')
        assert hasattr(StorageInterface, 'get_all_tasks')
        assert hasattr(StorageInterface, 'update_task')
        assert hasattr(StorageInterface, 'delete_task')
        assert hasattr(StorageInterface, 'clear_all')
    
    def test_cannot_instantiate_interface(self):
        """Test that StorageInterface cannot be instantiated directly."""
        from app.a2a_mvp.storage.interface import StorageInterface
        
        with pytest.raises(TypeError):
            StorageInterface()


class TestInMemoryStorage:
    """Test cases for in-memory storage implementation."""
    
    @pytest.fixture
    def storage(self):
        """Create an InMemoryStorage instance for testing."""
        from app.a2a_mvp.storage.memory import InMemoryStorage
        return InMemoryStorage()
    
    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        from app.a2a_mvp.core.types import Task
        return Task(
            id="test-123",
            title="Test Task",
            description="A test task",
            created_at=datetime.now()
        )
    
    def test_create_task(self, storage, sample_task):
        """Test creating a task in storage."""
        # Initially storage should be empty
        assert len(storage.get_all_tasks()) == 0
        
        # Create task
        created_task = storage.create_task(sample_task)
        
        # Verify task was created
        assert created_task.id == sample_task.id
        assert created_task.title == sample_task.title
        assert len(storage.get_all_tasks()) == 1
    
    def test_get_task(self, storage, sample_task):
        """Test retrieving a task from storage."""
        # Create task first
        storage.create_task(sample_task)
        
        # Retrieve task
        retrieved_task = storage.get_task(sample_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        assert retrieved_task.title == sample_task.title
    
    def test_get_nonexistent_task(self, storage):
        """Test retrieving a non-existent task."""
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        
        with pytest.raises(TaskNotFoundException) as exc_info:
            storage.get_task("nonexistent-id")
        
        assert exc_info.value.task_id == "nonexistent-id"
    
    def test_get_all_tasks(self, storage):
        """Test retrieving all tasks."""
        from app.a2a_mvp.core.types import Task
        
        # Create multiple tasks
        task1 = Task(id="1", title="Task 1", created_at=datetime.now())
        task2 = Task(id="2", title="Task 2", created_at=datetime.now())
        task3 = Task(id="3", title="Task 3", created_at=datetime.now())
        
        storage.create_task(task1)
        storage.create_task(task2)
        storage.create_task(task3)
        
        # Get all tasks
        all_tasks = storage.get_all_tasks()
        
        assert len(all_tasks) == 3
        assert any(t.id == "1" for t in all_tasks)
        assert any(t.id == "2" for t in all_tasks)
        assert any(t.id == "3" for t in all_tasks)
    
    def test_update_task(self, storage, sample_task):
        """Test updating a task."""
        # Create task first
        storage.create_task(sample_task)
        
        # Update task
        sample_task.title = "Updated Task"
        sample_task.completed = True
        sample_task.updated_at = datetime.now()
        
        updated_task = storage.update_task(sample_task)
        
        # Verify update
        assert updated_task.title == "Updated Task"
        assert updated_task.completed is True
        assert updated_task.updated_at is not None
        
        # Verify persistence
        retrieved_task = storage.get_task(sample_task.id)
        assert retrieved_task.title == "Updated Task"
        assert retrieved_task.completed is True
    
    def test_update_nonexistent_task(self, storage, sample_task):
        """Test updating a non-existent task."""
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        
        with pytest.raises(TaskNotFoundException):
            storage.update_task(sample_task)
    
    def test_delete_task(self, storage, sample_task):
        """Test deleting a task."""
        # Create task first
        storage.create_task(sample_task)
        assert len(storage.get_all_tasks()) == 1
        
        # Delete task
        storage.delete_task(sample_task.id)
        
        # Verify deletion
        assert len(storage.get_all_tasks()) == 0
        
        # Verify task is gone
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        with pytest.raises(TaskNotFoundException):
            storage.get_task(sample_task.id)
    
    def test_delete_nonexistent_task(self, storage):
        """Test deleting a non-existent task."""
        from app.a2a_mvp.core.exceptions import TaskNotFoundException
        
        with pytest.raises(TaskNotFoundException):
            storage.delete_task("nonexistent-id")
    
    def test_clear_all(self, storage):
        """Test clearing all tasks."""
        from app.a2a_mvp.core.types import Task
        
        # Create multiple tasks
        for i in range(5):
            task = Task(id=str(i), title=f"Task {i}", created_at=datetime.now())
            storage.create_task(task)
        
        assert len(storage.get_all_tasks()) == 5
        
        # Clear all
        storage.clear_all()
        
        # Verify all cleared
        assert len(storage.get_all_tasks()) == 0
    
    def test_storage_isolation(self):
        """Test that different storage instances are isolated."""
        from app.a2a_mvp.storage.memory import InMemoryStorage
        from app.a2a_mvp.core.types import Task
        
        storage1 = InMemoryStorage()
        storage2 = InMemoryStorage()
        
        # Add task to storage1
        task = Task(id="test", title="Test", created_at=datetime.now())
        storage1.create_task(task)
        
        # Verify isolation
        assert len(storage1.get_all_tasks()) == 1
        assert len(storage2.get_all_tasks()) == 0