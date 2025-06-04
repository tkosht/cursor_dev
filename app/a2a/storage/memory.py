"""
In-memory storage implementation for A2A MVP.
"""

from typing import Dict, List

from app.a2a.core.exceptions import TaskNotFoundException
from app.a2a.core.types import Task
from app.a2a.storage.interface import StorageInterface


class InMemoryStorage(StorageInterface):
    """In-memory implementation of task storage."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create_task(self, task: Task) -> Task:
        """Create a new task in storage."""
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Task:
        """Retrieve a task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundException(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks."""
        return list(self._tasks.values())

    def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        if task.id not in self._tasks:
            raise TaskNotFoundException(task.id)
        self._tasks[task.id] = task
        return task

    def delete_task(self, task_id: str) -> None:
        """Delete a task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundException(task_id)
        del self._tasks[task_id]

    def clear_all(self) -> None:
        """Clear all tasks from storage."""
        self._tasks.clear()
