"""
Pytest configuration for AMS tests
"""

import asyncio
import gc

# Add src to path
import sys
from pathlib import Path
from unittest.mock import MagicMock

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
def mock_config(monkeypatch):
    """Mock configuration for testing"""
    # Set test environment variables
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("AMS_MAX_PERSONAS", "10")
    monkeypatch.setenv("AMS_LOG_LEVEL", "DEBUG")

    # Import after env vars are set
    from config import get_config

    return get_config()


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    mock = MagicMock()
    mock.ainvoke = MagicMock(
        return_value=MagicMock(content='{"result": "test"}')
    )
    mock.invoke = MagicMock(
        return_value=MagicMock(content='{"result": "test"}')
    )
    return mock


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
def mock_websocket():
    """Mock websocket for testing"""
    mock = MagicMock()
    mock.send = MagicMock(return_value=asyncio.Future())
    mock.send.return_value.set_result(None)
    mock.recv = MagicMock(return_value=asyncio.Future())
    mock.recv.return_value.set_result('{"type": "test"}')
    return mock
