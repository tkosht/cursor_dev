"""
LLM factory for creating language models
"""

import logging
from typing import Optional, Any
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

# Optional import for Anthropic
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

from ..config import get_config, LLMProvider


logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create_gemini(model: str, **kwargs) -> BaseChatModel:
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
    def create_openai(model: str, **kwargs) -> BaseChatModel:
        """Create OpenAI model instance"""
        config = get_config()
        
        return ChatOpenAI(
            model=model,
            api_key=config.llm.openai_api_key,
            temperature=kwargs.get("temperature", config.llm.temperature),
            max_tokens=kwargs.get("max_tokens", config.llm.max_tokens),
            timeout=kwargs.get("timeout", config.llm.timeout),
            max_retries=kwargs.get("max_retries", 2),
        )
    
    @staticmethod 
    def create_anthropic(model: str, **kwargs) -> BaseChatModel:
        """Create Anthropic model instance"""
        if ChatAnthropic is None:
            raise ImportError(
                "langchain_anthropic is not installed. "
                "Install it with: pip install langchain-anthropic"
            )
        
        config = get_config()
        
        return ChatAnthropic(
            model=model,
            api_key=config.llm.anthropic_api_key,
            temperature=kwargs.get("temperature", config.llm.temperature),
            max_tokens=kwargs.get("max_tokens", config.llm.max_tokens),
            timeout=kwargs.get("timeout", config.llm.timeout),
            max_retries=kwargs.get("max_retries", 2),
        )
    
    @classmethod
    def create(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
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


@lru_cache(maxsize=4)
def create_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Create or get cached LLM instance
    
    This is a convenience function that caches LLM instances
    to avoid recreating them repeatedly.
    """
    # Convert kwargs to hashable format for caching
    cache_key = (
        provider,
        model,
        tuple(sorted(kwargs.items()))
    )
    
    return LLMFactory.create(provider, model, **kwargs)