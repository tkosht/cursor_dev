"""
Storage interface definition for A2A MVP.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.a2a_mvp.core.types import Task


class StorageInterface(ABC):
    """Abstract interface for task storage."""
    
    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """Create a new task in storage."""
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        """Retrieve a task by ID."""
        pass
    
    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks."""
        pass
    
    @abstractmethod
    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> None:
        """Delete a task by ID."""
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """Clear all tasks from storage."""
        pass