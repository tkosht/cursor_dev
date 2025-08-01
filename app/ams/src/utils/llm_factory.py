"""
LLM factory for creating language models
"""

import logging
from functools import lru_cache
from typing import Any, cast

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# Optional import for Anthropic
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

from ..config import get_config

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances"""

    @staticmethod
    def create_gemini(model: str, **kwargs: Any) -> BaseChatModel:
        """Create Gemini model instance"""
        config = get_config()

        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=config.llm.google_api_key,
            temperature=kwargs.get("temperature", config.llm.temperature),
            max_tokens=kwargs.get("max_tokens", config.llm.max_tokens),
            timeout=kwargs.get("timeout", config.llm.timeout),
            max_retries=kwargs.get("max_retries", 2),
        )

    @staticmethod
    def create_openai(model: str, **kwargs: Any) -> BaseChatModel:
        """Create OpenAI model instance"""
        config = get_config()

        api_key = None
        if config.llm.openai_api_key:
            api_key = SecretStr(config.llm.openai_api_key)

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=kwargs.get("temperature", config.llm.temperature),
            timeout=kwargs.get("timeout", config.llm.timeout),
            max_retries=kwargs.get("max_retries", 2),
        )

    @staticmethod
    def create_anthropic(model: str, **kwargs: Any) -> BaseChatModel:
        """Create Anthropic model instance"""
        if ChatAnthropic is None:
            raise ImportError(
                "langchain_anthropic is not installed. "
                "Install it with: pip install langchain-anthropic"
            )

        config = get_config()

        return cast(
            BaseChatModel,
            ChatAnthropic(
                model=model,
                api_key=config.llm.anthropic_api_key,
                temperature=kwargs.get("temperature", config.llm.temperature),
                max_tokens=kwargs.get("max_tokens", config.llm.max_tokens),
                timeout=kwargs.get("timeout", config.llm.timeout),
                max_retries=kwargs.get("max_retries", 2),
            ),
        )

    @classmethod
    def create(
        cls, provider: str | None = None, model: str | None = None, **kwargs: Any
    ) -> BaseChatModel:
        """
        Create LLM instance

        Args:
            provider: LLM provider (gemini, openai, anthropic)
            model: Model name
            **kwargs: Additional model parameters

        Returns:
            LLM instance
        """
        config = get_config()

        # Use defaults from config if not specified
        if provider is None:
            provider = config.llm.provider
        if model is None:
            # Get default model for provider
            model_map = {
                "gemini": config.llm.gemini_model,
                "openai": config.llm.openai_model,
                "anthropic": config.llm.anthropic_model,
            }
            model = model_map.get(provider, "gemini-2.5-flash")

        # Create model based on provider
        provider_map = {
            "gemini": cls.create_gemini,
            "openai": cls.create_openai,
            "anthropic": cls.create_anthropic,
        }

        if provider not in provider_map:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"Creating LLM: {provider}/{model}")
        return provider_map[provider](model, **kwargs)


def create_llm(
    provider: str | None = None, model: str | None = None, **kwargs: Any
) -> BaseChatModel:
    """
    Create or get cached LLM instance

    This is a convenience function that caches LLM instances
    to avoid recreating them repeatedly.

    Note: Caching is disabled by default due to gRPC connection issues
    in test environments. Set use_cache=True to enable caching.
    """
    use_cache = kwargs.pop("use_cache", False)

    if use_cache:
        # Use a cached version if caching is enabled
        return _create_llm_cached(provider, model, **kwargs)
    else:
        # Create a new instance without caching
        return LLMFactory.create(provider, model, **kwargs)


@lru_cache(maxsize=4)
def _create_llm_cached(
    provider: str | None = None, model: str | None = None, **kwargs: Any
) -> BaseChatModel:
    """Internal cached version of create_llm"""
    return LLMFactory.create(provider, model, **kwargs)
