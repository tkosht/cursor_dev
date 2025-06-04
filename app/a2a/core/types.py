"""
Core type definitions for A2A MVP.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """Represents a TODO task."""

    id: str
    title: str
    created_at: datetime
    description: Optional[str] = None
    completed: bool = False
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary representation."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary representation."""
        # Convert ISO format strings to datetime objects
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at") and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class TaskRequest:
    """Represents a request to perform an action on tasks."""

    action: str  # create, read, update, delete, list
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None


@dataclass
class TaskResponse:
    """Represents a response from task operations."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class A2ACapabilities:
    """A2A agent capabilities."""

    streaming: bool = False
    push_notifications: bool = False


@dataclass
class A2ASkill:
    """Represents an A2A agent skill."""

    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]


@dataclass
class A2AAgentCard:
    """Represents an A2A agent card."""

    name: str
    description: str
    version: str
    url: str
    capabilities: A2ACapabilities
    skills: List[A2ASkill]
