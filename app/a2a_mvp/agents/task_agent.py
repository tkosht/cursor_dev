"""
Task management agent for A2A MVP.
"""
from typing import Dict, Any

from app.a2a_mvp.agents.base import BaseAgent
from app.a2a_mvp.core.types import (
    A2AAgentCard, A2ACapabilities, A2ASkill,
    TaskRequest, TaskResponse
)
from app.a2a_mvp.skills.task_skills import TaskSkill
from app.a2a_mvp.storage.interface import StorageInterface


class TaskAgent(BaseAgent):
    """Agent for managing TODO tasks."""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.task_skill = TaskSkill(storage)
    
    def get_agent_card(self) -> A2AAgentCard:
        """Get the agent card describing this agent's capabilities."""
        capabilities = A2ACapabilities(
            streaming=False,
            push_notifications=False
        )
        
        skills = [
            A2ASkill(
                id="create_task",
                name="Create Task",
                description="Create a new TODO task",
                tags=["task", "create", "todo"],
                examples=["Create a task to buy groceries", "Add new task: Complete project"]
            ),
            A2ASkill(
                id="list_tasks",
                name="List Tasks",
                description="List all TODO tasks",
                tags=["task", "list", "todo"],
                examples=["Show all tasks", "What tasks do I have?"]
            ),
            A2ASkill(
                id="update_task",
                name="Update Task",
                description="Update an existing task",
                tags=["task", "update", "todo"],
                examples=["Update task title", "Mark task as complete"]
            ),
            A2ASkill(
                id="delete_task",
                name="Delete Task",
                description="Delete a task",
                tags=["task", "delete", "todo"],
                examples=["Delete task", "Remove completed task"]
            ),
            A2ASkill(
                id="toggle_completion",
                name="Toggle Task Completion",
                description="Toggle task completion status",
                tags=["task", "complete", "toggle"],
                examples=["Mark task as done", "Toggle task completion"]
            ),
            A2ASkill(
                id="clear_all",
                name="Clear All Tasks",
                description="Clear all tasks",
                tags=["task", "clear", "all"],
                examples=["Clear all tasks", "Delete everything"]
            )
        ]
        
        return A2AAgentCard(
            name="Task Manager Agent",
            description="An agent for managing TODO tasks",
            version="1.0.0",
            url="http://localhost:8000",
            capabilities=capabilities,
            skills=skills
        )
    
    def process_request(self, request: TaskRequest) -> TaskResponse:
        """Process an incoming task request."""
        try:
            # Route based on action
            if request.action == "create":
                result = self.task_skill.create_task(request.data or {})
            elif request.action == "get":
                result = self.task_skill.get_task(request.task_id)
            elif request.action == "list":
                result = self.task_skill.list_tasks()
            elif request.action == "update":
                result = self.task_skill.update_task(request.task_id, request.data or {})
            elif request.action == "delete":
                result = self.task_skill.delete_task(request.task_id)
            elif request.action == "toggle":
                result = self.task_skill.toggle_completion(request.task_id)
            elif request.action == "clear":
                result = self.task_skill.clear_all_tasks()
            else:
                return TaskResponse(
                    success=False,
                    error=f"Invalid action: {request.action}"
                )
            
            # Convert skill result to TaskResponse
            if result["success"]:
                # Extract the appropriate data based on action
                if request.action == "list":
                    data = result  # Return the whole result for list
                elif request.action in ["delete", "clear"]:
                    data = result  # Return message
                else:
                    data = result.get("task")  # Return task data
                
                return TaskResponse(success=True, data=data)
            else:
                return TaskResponse(
                    success=False,
                    error=result.get("error", "Unknown error")
                )
        
        except Exception as e:
            return TaskResponse(
                success=False,
                error=f"Internal error: {str(e)}"
            )
    
    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A protocol message."""
        try:
            # Validate message format
            if "action" not in message:
                return {
                    "success": False,
                    "error": "Missing required field: action"
                }
            
            # Create TaskRequest from message
            request = TaskRequest(
                action=message["action"],
                data=message.get("data"),
                task_id=message.get("task_id")
            )
            
            # Process request
            response = self.process_request(request)
            
            # Convert response to dict
            return {
                "success": response.success,
                "data": response.data,
                "error": response.error
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to handle message: {str(e)}"
            }