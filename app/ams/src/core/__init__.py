"""
AMS Core Module - Core interfaces and base classes
"""

from .base import (
    BaseAction,
    BaseAgent,
    BaseEnvironment,
    BasePlugin,
    BaseSimulation,
)
from .interfaces import (
    IAction,
    IAgent,
    IEnvironment,
    IPlugin,
    ISimulation,
    IVisualization,
)
from .types import (
    ActionResult,
    AgentID,
    EvaluationResult,
    PersonaAttributes,
    SimulationState,
)

__all__ = [
    # Interfaces
    "IAgent",
    "IEnvironment",
    "IAction",
    "IPlugin",
    "ISimulation",
    "IVisualization",
    # Base Classes
    "BaseAgent",
    "BaseEnvironment",
    "BaseAction",
    "BasePlugin",
    "BaseSimulation",
    # Types
    "AgentID",
    "SimulationState",
    "ActionResult",
    "PersonaAttributes",
    "EvaluationResult",
]
