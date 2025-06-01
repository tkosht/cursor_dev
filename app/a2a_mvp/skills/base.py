"""
Base skill class for A2A MVP.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSkill(ABC):
    """Abstract base class for skills."""
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill with given parameters."""
        pass
    
    def validate_params(self, required: list, params: dict) -> tuple[bool, str]:
        """Validate that required parameters are present."""
        missing = [p for p in required if p not in params or params[p] is None]
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"
        return True, ""