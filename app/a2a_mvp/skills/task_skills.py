"""
Task management skills for A2A MVP.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.a2a_mvp.skills.base import BaseSkill
from app.a2a_mvp.storage.interface import StorageInterface
from app.a2a_mvp.core.types import Task
from app.a2a_mvp.core.exceptions import TaskNotFoundException, InvalidTaskDataException


class TaskSkill(BaseSkill):
    """Skill for managing tasks."""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Route to appropriate task operation."""
        action = kwargs.get('action', 'list')
        
        if action == 'create':
            return self.create_task(kwargs.get('data', {}))
        elif action == 'get':
            return self.get_task(kwargs.get('task_id'))
        elif action == 'list':
            return self.list_tasks()
        elif action == 'update':
            return self.update_task(kwargs.get('task_id'), kwargs.get('data', {}))
        elif action == 'delete':
            return self.delete_task(kwargs.get('task_id'))
        elif action == 'toggle':
            return self.toggle_completion(kwargs.get('task_id'))
        elif action == 'clear':
            return self.clear_all_tasks()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        try:
            # Validate required fields
            if 'title' not in data or not data['title']:
                return {"success": False, "error": "Title is required"}
            
            # Create task
            task = Task(
                id=str(uuid.uuid4()),
                title=data['title'],
                description=data.get('description'),
                created_at=datetime.now()
            )
            
            created_task = self.storage.create_task(task)
            return {
                "success": True,
                "task": created_task.to_dict()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_task(self, task_id: Optional[str]) -> Dict[str, Any]:
        """Get a task by ID."""
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            task = self.storage.get_task(task_id)
            return {
                "success": True,
                "task": task.to_dict()
            }
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_tasks(self) -> Dict[str, Any]:
        """List all tasks."""
        try:
            tasks = self.storage.get_all_tasks()
            return {
                "success": True,
                "tasks": [task.to_dict() for task in tasks],
                "count": len(tasks)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_task(self, task_id: Optional[str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            # Get existing task
            task = self.storage.get_task(task_id)
            
            # Update fields
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'completed' in data:
                task.completed = data['completed']
            
            task.updated_at = datetime.now()
            
            updated_task = self.storage.update_task(task)
            return {
                "success": True,
                "task": updated_task.to_dict()
            }
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_task(self, task_id: Optional[str]) -> Dict[str, Any]:
        """Delete a task."""
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            self.storage.delete_task(task_id)
            return {
                "success": True,
                "message": f"Task {task_id} deleted successfully"
            }
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_completion(self, task_id: Optional[str]) -> Dict[str, Any]:
        """Toggle task completion status."""
        try:
            if not task_id:
                return {"success": False, "error": "Task ID is required"}
            
            task = self.storage.get_task(task_id)
            task.completed = not task.completed
            task.updated_at = datetime.now()
            
            updated_task = self.storage.update_task(task)
            return {
                "success": True,
                "task": updated_task.to_dict()
            }
        except TaskNotFoundException:
            return {"success": False, "error": f"Task not found: {task_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def clear_all_tasks(self) -> Dict[str, Any]:
        """Clear all tasks."""
        try:
            self.storage.clear_all()
            return {
                "success": True,
                "message": "All tasks cleared successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}