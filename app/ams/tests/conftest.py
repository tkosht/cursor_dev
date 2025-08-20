"""
Pytest configuration for AMS tests
"""

import asyncio
import gc
import os

# Add src to path
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# NO MOCKS - Following CLAUDE.md mandatory rules
# from unittest.mock import MagicMock  # REMOVED - Real APIs only

import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function.

    This implementation handles the event loop closure issue that occurs when
    running async tests in batch mode. Changed to function scope to ensure
    clean state between tests, especially for gRPC connections.
    """
    # Create a new event loop for each test
    loop = asyncio.get_event_loop_policy().new_event_loop()

    # Set the event loop for the current policy
    asyncio.set_event_loop(loop)

    yield loop

    # Cleanup after test
    try:
        # Cancel all pending tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            if not task.done():
                task.cancel()

        # Wait for all tasks to be cancelled
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        # Force garbage collection to clean up gRPC resources
        gc.collect()

        # Small delay to ensure gRPC cleanup
        loop.run_until_complete(asyncio.sleep(0.1))

    finally:
        # Close the loop
        loop.close()
        # Set event loop to None to ensure fresh start
        asyncio.set_event_loop(None)
        # Force garbage collection again after loop closure
        gc.collect()


@pytest.fixture
def test_config(monkeypatch):
    """Test configuration with real API keys"""
    # Load test environment from .env.test
    from pathlib import Path

    from dotenv import load_dotenv

    test_env_path = Path(__file__).parent.parent / ".env.test"
    if test_env_path.exists():
        load_dotenv(test_env_path, override=True)

    # TEST_MODE は廃止。実APIキーで実行する前提。

    # Verify API key is set (fail fast if not)
    provider = os.getenv("TEST_LLM_PROVIDER", "gemini")
    if provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set - cannot run tests with real API")
    elif provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - cannot run tests with real API")
    elif provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set - cannot run tests with real API")

    # Import after env vars are set
    from config import get_config

    return get_config()


@pytest.fixture
def real_llm():
    """Real LLM for testing - NO MOCKS ALLOWED"""
    from llm_test_helper import get_llm_helper

    return get_llm_helper()


@pytest.fixture
def sample_article():
    """Sample article for testing"""
    return """
    # Introduction to Large Language Models

    Large Language Models (LLMs) have revolutionized natural language processing
    and artificial intelligence. These models, trained on vast amounts of text data,
    can understand and generate human-like text with remarkable accuracy.

    ## Key Capabilities

    - Text generation and completion
    - Language translation
    - Question answering
    - Code generation
    - Summarization

    ## Applications

    LLMs are being used across various industries:

    1. **Healthcare**: Medical documentation and research
    2. **Education**: Personalized tutoring and content creation
    3. **Business**: Customer service and content marketing
    4. **Technology**: Code assistance and debugging

    ## Future Directions

    The future of LLMs looks promising with ongoing research in:
    - Multimodal capabilities
    - Improved efficiency
    - Better reasoning abilities
    - Enhanced safety and alignment

    As these models continue to evolve, we can expect even more
    innovative applications and improvements in human-AI interaction.
    """


@pytest.fixture
def sample_persona_attributes():
    """Sample persona attributes for testing"""
    from core.types import (
        InformationChannel,
        PersonaAttributes,
        PersonalityType,
    )

    return PersonaAttributes(
        age=35,
        occupation="Software Engineer",
        location="San Francisco, CA",
        education_level="Master's Degree",
        values=["innovation", "efficiency", "learning"],
        interests=["technology", "AI", "startups"],
        personality_traits={
            PersonalityType.OPENNESS: 0.8,
            PersonalityType.CONSCIENTIOUSNESS: 0.7,
        },
        information_seeking_behavior="active",
        preferred_channels=[
            InformationChannel.TECH_BLOGS,
            InformationChannel.SOCIAL_MEDIA,
        ],
    )


@pytest.fixture
def test_websocket():
    """Test websocket fixture - real implementation preferred"""
    # For websocket, we can use a test implementation since it's not an LLM
    # This is for internal communication, not external API mocking
    import asyncio

    class TestWebSocket:
        def __init__(self):
            self.messages = []
            self.closed = False

        async def send(self, message):
            if self.closed:
                raise ConnectionError("WebSocket is closed")
            self.messages.append(message)

        async def recv(self):
            if self.closed:
                raise ConnectionError("WebSocket is closed")
            await asyncio.sleep(0.01)  # Simulate network delay
            return '{"type": "test", "data": {}}'

        async def close(self):
            self.closed = True

    return TestWebSocket()
