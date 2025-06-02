"""
Base agent class for A2A MVP.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.a2a_mvp.core.types import A2AAgentCard, TaskRequest, TaskResponse


class BaseAgent(ABC):
    """Abstract base class for A2A agents."""

    @abstractmethod
    def get_agent_card(self) -> A2AAgentCard:
        """Get the agent card describing this agent's capabilities."""
        pass

    @abstractmethod
    def process_request(self, request: TaskRequest) -> TaskResponse:
        """Process an incoming task request."""
        pass

    @abstractmethod
    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A protocol message."""
        pass
