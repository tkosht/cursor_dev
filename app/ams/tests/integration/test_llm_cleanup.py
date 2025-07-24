"""
LLM Connection Cleanup Fixture

Provides proper cleanup for Google Gemini API gRPC connections
to prevent "Event loop is closed" errors in async tests.
"""

import asyncio
import gc
import logging
from typing import AsyncGenerator

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


async def cleanup_grpc_connections():
    """Force cleanup of gRPC connections and pending tasks"""
    # Get current event loop
    loop = asyncio.get_event_loop()
    
    # Get all tasks
    tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    
    if tasks:
        logger.debug(f"Cancelling {len(tasks)} pending tasks")
        # Cancel all pending tasks
        for task in tasks:
            task.cancel()
        
        # Wait for all tasks to be cancelled
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # Force garbage collection to clean up gRPC resources
    gc.collect()
    
    # Small delay to ensure cleanup
    await asyncio.sleep(0.1)


@pytest.fixture
async def llm_with_cleanup() -> AsyncGenerator:
    """Create LLM instance with proper cleanup"""
    from src.utils.llm_factory import create_llm
    
    llm = create_llm()
    yield llm
    
    # Cleanup after test
    await cleanup_grpc_connections()
    
    # If LLM is ChatGoogleGenerativeAI, ensure client is cleaned up
    if isinstance(llm, ChatGoogleGenerativeAI):
        # Access internal client to ensure it's properly closed
        if hasattr(llm, '_client'):
            try:
                # Close any open connections
                if hasattr(llm._client, 'close'):
                    await llm._client.close()
            except Exception as e:
                logger.debug(f"Error closing LLM client: {e}")