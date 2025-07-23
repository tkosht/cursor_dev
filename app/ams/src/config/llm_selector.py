"""
LLM automatic selection based on task requirements
"""

import logging
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers"""

    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class TaskType(str, Enum):
    """Types of tasks for LLM selection"""

    ANALYSIS = "analysis"
    GENERATION = "generation"
    EVALUATION = "evaluation"
    SUMMARIZATION = "summarization"
    REASONING = "reasoning"
    CREATIVE = "creative"


class LLMCapabilities(BaseModel):
    """Capabilities of an LLM model"""

    provider: LLMProvider
    model: str

    # Performance characteristics
    speed: float = Field(ge=0.0, le=10.0, description="Speed rating 0-10")
    quality: float = Field(ge=0.0, le=10.0, description="Quality rating 0-10")
    cost_per_1k_tokens: float = Field(
        ge=0.0, description="Cost per 1000 tokens"
    )

    # Technical capabilities
    max_tokens: int = Field(gt=0)
    supports_json_mode: bool = Field(default=False)
    supports_function_calling: bool = Field(default=False)
    supports_vision: bool = Field(default=False)

    # Task suitability (0-10)
    task_scores: dict[TaskType, float] = Field(default_factory=dict)


# Predefined model capabilities
MODEL_CAPABILITIES = {
    # Gemini models
    "gemini-2.5-flash": LLMCapabilities(
        provider=LLMProvider.GEMINI,
        model="gemini-2.5-flash",
        speed=9.5,
        quality=8.5,
        cost_per_1k_tokens=0.0001,
        max_tokens=1048576,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 8.5,
            TaskType.GENERATION: 9.0,
            TaskType.EVALUATION: 8.0,
            TaskType.SUMMARIZATION: 9.0,
            TaskType.REASONING: 8.0,
            TaskType.CREATIVE: 8.5,
        },
    ),
    "gemini-2.5-pro": LLMCapabilities(
        provider=LLMProvider.GEMINI,
        model="gemini-2.5-pro",
        speed=7.0,
        quality=9.5,
        cost_per_1k_tokens=0.001,
        max_tokens=1048576,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 9.5,
            TaskType.GENERATION: 9.5,
            TaskType.EVALUATION: 9.5,
            TaskType.SUMMARIZATION: 9.0,
            TaskType.REASONING: 9.5,
            TaskType.CREATIVE: 9.0,
        },
    ),
    # OpenAI models
    "gpt-4o-mini": LLMCapabilities(
        provider=LLMProvider.OPENAI,
        model="gpt-4o-mini",
        speed=9.0,
        quality=8.0,
        cost_per_1k_tokens=0.00015,
        max_tokens=128000,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 8.0,
            TaskType.GENERATION: 8.5,
            TaskType.EVALUATION: 7.5,
            TaskType.SUMMARIZATION: 8.5,
            TaskType.REASONING: 7.5,
            TaskType.CREATIVE: 8.0,
        },
    ),
    "gpt-4o": LLMCapabilities(
        provider=LLMProvider.OPENAI,
        model="gpt-4o",
        speed=7.5,
        quality=9.5,
        cost_per_1k_tokens=0.0025,
        max_tokens=128000,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 9.5,
            TaskType.GENERATION: 9.5,
            TaskType.EVALUATION: 9.0,
            TaskType.SUMMARIZATION: 9.0,
            TaskType.REASONING: 9.5,
            TaskType.CREATIVE: 9.0,
        },
    ),
    # Anthropic models
    "claude-3-haiku-20240307": LLMCapabilities(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-haiku-20240307",
        speed=9.5,
        quality=8.0,
        cost_per_1k_tokens=0.00025,
        max_tokens=200000,
        supports_json_mode=False,
        supports_function_calling=False,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 8.0,
            TaskType.GENERATION: 8.0,
            TaskType.EVALUATION: 7.5,
            TaskType.SUMMARIZATION: 8.5,
            TaskType.REASONING: 7.5,
            TaskType.CREATIVE: 7.5,
        },
    ),
    "claude-3-5-sonnet-20241022": LLMCapabilities(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-5-sonnet-20241022",
        speed=7.0,
        quality=9.5,
        cost_per_1k_tokens=0.003,
        max_tokens=200000,
        supports_json_mode=False,
        supports_function_calling=False,
        supports_vision=True,
        task_scores={
            TaskType.ANALYSIS: 9.5,
            TaskType.GENERATION: 9.5,
            TaskType.EVALUATION: 9.5,
            TaskType.SUMMARIZATION: 9.0,
            TaskType.REASONING: 9.5,
            TaskType.CREATIVE: 9.5,
        },
    ),
}


class LLMSelector:
    """Automatic LLM selection based on task requirements"""

    def __init__(self, available_providers: list[LLMProvider] | None = None):
        """
        Initialize selector with available providers

        Args:
            available_providers: List of providers with valid API keys
        """
        self.available_providers = (
            available_providers
            if available_providers is not None
            else list(LLMProvider)
        )
        self.model_capabilities = MODEL_CAPABILITIES

    def select_model(
        self,
        task_type: TaskType,
        required_features: list[str] | None = None,
        max_cost_per_1k: float | None = None,
        min_quality: float = 7.0,
        min_speed: float = 7.0,
        prefer_provider: LLMProvider | None = None,
    ) -> tuple[str, LLMCapabilities]:
        """
        Select optimal model based on requirements

        Args:
            task_type: Type of task to perform
            required_features: Required features (e.g., "json_mode", "function_calling")
            max_cost_per_1k: Maximum acceptable cost per 1000 tokens
            min_quality: Minimum quality score required
            min_speed: Minimum speed score required
            prefer_provider: Preferred provider if available

        Returns:
            Tuple of (model_name, capabilities)
        """
        required_features = required_features or []
        candidates = []

        for model_name, capabilities in self.model_capabilities.items():
            # Check if provider is available
            if capabilities.provider not in self.available_providers:
                continue

            # Check required features
            if (
                "json_mode" in required_features
                and not capabilities.supports_json_mode
            ):
                continue
            if (
                "function_calling" in required_features
                and not capabilities.supports_function_calling
            ):
                continue
            if (
                "vision" in required_features
                and not capabilities.supports_vision
            ):
                continue

            # Check cost constraint
            if (
                max_cost_per_1k
                and capabilities.cost_per_1k_tokens > max_cost_per_1k
            ):
                continue

            # Check quality and speed minimums
            if (
                capabilities.quality < min_quality
                or capabilities.speed < min_speed
            ):
                continue

            # Calculate task suitability score
            capabilities.task_scores.get(task_type, 5.0)

            # Calculate overall score
            overall_score = self._calculate_score(
                capabilities,
                task_type,
                prefer_provider,
            )

            candidates.append((model_name, capabilities, overall_score))

        if not candidates:
            # Fallback to default
            logger.warning("No suitable model found, using default")
            return (
                "gemini-2.5-flash",
                self.model_capabilities["gemini-2.5-flash"],
            )

        # Sort by score and return best
        candidates.sort(key=lambda x: x[2], reverse=True)
        best_model, best_capabilities, _ = candidates[0]

        logger.info(f"Selected model: {best_model} for task: {task_type}")
        return best_model, best_capabilities

    def _calculate_score(
        self,
        capabilities: LLMCapabilities,
        task_type: TaskType,
        prefer_provider: LLMProvider | None,
    ) -> float:
        """Calculate overall score for model selection"""
        # Base score from task suitability
        task_score = capabilities.task_scores.get(task_type, 5.0)

        # Weighted combination
        score = (
            task_score * 0.4
            + capabilities.quality * 0.3
            + capabilities.speed * 0.2
            + (10 - capabilities.cost_per_1k_tokens * 1000)
            * 0.1  # Cost inverse
        )

        # Provider preference bonus
        if prefer_provider and capabilities.provider == prefer_provider:
            score += 1.0

        return score

    def estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for a specific model and token count"""
        if model_name not in self.model_capabilities:
            return 0.0

        capabilities = self.model_capabilities[model_name]
        total_tokens = input_tokens + output_tokens
        cost = (total_tokens / 1000) * capabilities.cost_per_1k_tokens

        return cost


def select_optimal_llm(
    task_type: TaskType,
    required_features: list[str] | None = None,
    budget_constraint: float | None = None,
) -> tuple[str, str]:
    """
    Convenience function to select optimal LLM

    Returns:
        Tuple of (provider, model_name)
    """
    from .config import get_config

    config = get_config()

    # Determine available providers based on API keys
    available_providers = []
    if config.llm.google_api_key:
        available_providers.append(LLMProvider.GEMINI)
    if config.llm.openai_api_key:
        available_providers.append(LLMProvider.OPENAI)
    if config.llm.anthropic_api_key:
        available_providers.append(LLMProvider.ANTHROPIC)

    selector = LLMSelector(available_providers)

    model_name, capabilities = selector.select_model(
        task_type=task_type,
        required_features=required_features,
        max_cost_per_1k=budget_constraint,
        prefer_provider=(
            LLMProvider(config.llm.provider) if config.llm.provider else None
        ),
    )

    return capabilities.provider.value, model_name
