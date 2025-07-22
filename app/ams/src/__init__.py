"""
Article Market Simulator (AMS) package
"""

from .core import (
    IAgent,
    IEnvironment,
    IAction,
    IPlugin,
    ISimulation,
    BaseAgent,
    BaseEnvironment,
    BaseAction,
    BasePlugin,
    BaseSimulation,
)

from .agents import (
    OrchestratorAgent,
    ArticleReviewState,
)

from .config import (
    AMSConfig,
    get_config,
    LLMProvider,
    TaskType,
    select_optimal_llm,
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