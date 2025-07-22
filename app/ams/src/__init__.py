"""
Article Market Simulator (AMS) package
"""

from .agents import (
    ArticleReviewState,
    OrchestratorAgent,
)
from .config import (
    AMSConfig,
    LLMProvider,
    TaskType,
    get_config,
    select_optimal_llm,
)
from .core import (
    BaseAction,
    BaseAgent,
    BaseEnvironment,
    BasePlugin,
    BaseSimulation,
    IAction,
    IAgent,
    IEnvironment,
    IPlugin,
    ISimulation,
)

__version__ = "0.1.0"

__all__ = [
    # Core interfaces
    "IAgent",
    "IEnvironment",
    "IAction",
    "IPlugin",
    "ISimulation",
    # Base implementations
    "BaseAgent",
    "BaseEnvironment",
    "BaseAction",
    "BasePlugin",
    "BaseSimulation",
    # Agents
    "OrchestratorAgent",
    "ArticleReviewState",
    # Config
    "AMSConfig",
    "get_config",
    "LLMProvider",
    "TaskType",
    "select_optimal_llm",
]
