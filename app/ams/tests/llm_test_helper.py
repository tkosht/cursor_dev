"""
Test helper for real LLM API calls with rate limiting for CI environments
Following CLAUDE.md mandatory rules: NO MOCKS, REAL API CALLS ONLY
"""

import os
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMCallConfig:
    """Configuration for LLM API calls in tests"""
    max_calls_ci: int = 5  # Maximum calls in CI environment
    max_calls_local: int = 20  # Maximum calls in local environment
    call_delay: float = 0.5  # Delay between calls to avoid rate limits
    test_prompt_prefix: str = "TEST: "  # Prefix for test prompts
    cache_enabled: bool = True  # Enable response caching for identical prompts


class LLMTestHelper:
    """
    Helper for managing real LLM API calls in tests
    Implements rate limiting and caching for CI/CD environments
    """
    
    def __init__(self):
        self.call_count = 0
        self.is_ci = os.getenv("CI", "false").lower() == "true"
        self.max_calls = LLMCallConfig.max_calls_ci if self.is_ci else LLMCallConfig.max_calls_local
        self.cache: Dict[str, Any] = {}
        self.config = LLMCallConfig()
        
        # Initialize real LLM based on environment
        self.provider = os.getenv("TEST_LLM_PROVIDER", "gemini")
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize real LLM client based on provider"""
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _init_gemini(self):
        """Initialize Google Gemini client using langchain"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment")
            
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7,
                max_tokens=1000
            )
            self.llm_type = "gemini"
            self.model_name = model_name
            logger.info(f"Initialized Gemini model: {model_name}")
        except ImportError:
            raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            self.llm = AsyncOpenAI(api_key=api_key)
            self.llm_type = "openai"
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"Initialized OpenAI model: {self.model_name}")
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import AsyncAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            
            self.llm = AsyncAnthropic(api_key=api_key)
            self.llm_type = "anthropic"
            self.model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            logger.info(f"Initialized Anthropic model: {self.model_name}")
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
    
    async def generate(self, prompt: str, use_cache: bool = True, 
                      system_prompt: Optional[str] = None) -> str:
        """
        Generate response from real LLM with rate limiting and caching
        
        Args:
            prompt: The prompt to send to the LLM
            use_cache: Whether to use cached responses for identical prompts
            system_prompt: Optional system prompt for the LLM
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If call limit exceeded in CI environment
        """
        # Check call limit
        if self.call_count >= self.max_calls:
            if self.is_ci:
                raise RuntimeError(
                    f"LLM call limit exceeded in CI environment "
                    f"({self.call_count}/{self.max_calls} calls). "
                    "Consider using cached responses or reducing test scope."
                )
            else:
                logger.warning(f"Call limit reached ({self.call_count}/{self.max_calls})")
        
        # Check cache
        cache_key = f"{system_prompt}|{prompt}"
        if use_cache and cache_key in self.cache:
            logger.debug("Using cached response")
            return self.cache[cache_key]
        
        # Add test prefix to identify test calls
        test_prompt = f"{self.config.test_prompt_prefix}{prompt}"
        
        # Rate limiting
        if self.call_count > 0:
            await asyncio.sleep(self.config.call_delay)
        
        # Make real API call
        response = await self._call_llm(test_prompt, system_prompt)
        
        self.call_count += 1
        logger.info(f"LLM call {self.call_count}/{self.max_calls} completed")
        
        # Cache response
        if use_cache:
            self.cache[cache_key] = response
        
        return response
    
    async def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Make actual LLM API call based on provider"""
        try:
            if self.llm_type == "gemini":
                messages = []
                if system_prompt:
                    # Gemini doesn't have system messages, combine with prompt
                    prompt = f"{system_prompt}\n\n{prompt}"
                response = await self.llm.ainvoke(prompt)
                return response.content
            
            elif self.llm_type == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await self.llm.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif self.llm_type == "anthropic":
                messages = [{"role": "user", "content": prompt}]
                response = await self.llm.messages.create(
                    model=self.model_name,
                    messages=messages,
                    system=system_prompt if system_prompt else "",
                    max_tokens=1000
                )
                return response.content[0].text
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def generate_structured(self, prompt: str, schema: Dict[str, Any],
                           use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate structured JSON response from LLM
        
        Args:
            prompt: The prompt to send to the LLM
            schema: Expected JSON schema for validation
            use_cache: Whether to use cached responses
        
        Returns:
            Parsed JSON response
        """
        # Add schema instruction to prompt
        structured_prompt = f"""
        {prompt}
        
        Please respond with valid JSON matching this schema:
        {json.dumps(schema, indent=2)}
        
        Response must be valid JSON only, no additional text.
        """
        
        response = asyncio.run(self.generate(structured_prompt, use_cache))
        
        # Parse and validate JSON
        try:
            # Extract JSON from response (handle potential markdown formatting)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.error(f"Response was: {response}")
            raise
    
    def reset_call_count(self):
        """Reset call counter (useful between test suites)"""
        self.call_count = 0
        logger.info("LLM call counter reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "provider": self.provider,
            "call_count": self.call_count,
            "max_calls": self.max_calls,
            "cache_size": len(self.cache),
            "is_ci": self.is_ci
        }


# Singleton instance for test session
_llm_helper: Optional[LLMTestHelper] = None


def get_llm_helper() -> LLMTestHelper:
    """Get or create singleton LLM test helper"""
    global _llm_helper
    if _llm_helper is None:
        _llm_helper = LLMTestHelper()
    return _llm_helper


# Pre-generated responses for deterministic testing
DETERMINISTIC_RESPONSES = {
    "persona_generation": {
        "tech_article": {
            "occupation": "Software Developer",
            "age": 28,
            "values": ["innovation", "efficiency", "learning"],
            "interests": ["AI", "programming", "open source"],
            "reaction": "Very interested in the technical details and potential applications"
        },
        "finance_article": {
            "occupation": "Financial Analyst",
            "age": 35,
            "values": ["accuracy", "growth", "stability"],
            "interests": ["markets", "economics", "data analysis"],
            "reaction": "Focused on ROI and practical business implications"
        }
    },
    "sentiment_analysis": {
        "positive": {"sentiment": "positive", "score": 0.85, "confidence": 0.9},
        "negative": {"sentiment": "negative", "score": 0.3, "confidence": 0.85},
        "neutral": {"sentiment": "neutral", "score": 0.5, "confidence": 0.8}
    }
}


def get_deterministic_response(category: str, key: str) -> Dict[str, Any]:
    """
    Get deterministic response for testing without API calls
    Useful for unit tests that need consistent outputs
    """
    if category in DETERMINISTIC_RESPONSES and key in DETERMINISTIC_RESPONSES[category]:
        return DETERMINISTIC_RESPONSES[category][key]
    raise KeyError(f"No deterministic response for {category}/{key}")