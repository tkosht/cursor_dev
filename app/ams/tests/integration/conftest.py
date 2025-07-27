"""Integration test configuration"""

import asyncio
import gc
import warnings
import os

import pytest


@pytest.fixture(scope="function")
def event_loop():
    """Create a new event loop for each test function."""
    # Set environment variable to allow tests to know they're in batch mode
    os.environ['PYTEST_BATCH_RUN'] = '1'
    
    # Close any existing loop
    try:
        loop = asyncio.get_running_loop()
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass
    
    # Create new loop with custom exception handler
    loop = asyncio.new_event_loop()
    
    # Suppress gRPC warnings
    def exception_handler(loop, context):
        exception = context.get('exception')
        if exception and 'grpc' in str(exception):
            return  # Ignore gRPC exceptions during cleanup
        # Log other exceptions
        loop.default_exception_handler(context)
    
    loop.set_exception_handler(exception_handler)
    asyncio.set_event_loop(loop)
    
    yield loop
    
    # Cleanup after test
    try:
        # Get all tasks
        pending = asyncio.all_tasks(loop)
    except AttributeError:
        # Python 3.9+
        pending = asyncio.tasks.all_tasks(loop)
    
    # Cancel all pending tasks
    for task in pending:
        if not task.done():
            task.cancel()
    
    # Wait for task cancellation
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    
    # Additional cleanup wait
    loop.run_until_complete(asyncio.sleep(0.5))
    
    # Close the loop
    loop.close()
    asyncio.set_event_loop(None)
    
    # Force garbage collection
    gc.collect()


@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Clean up after each test"""
    # Run the test
    yield
    
    # Import here to avoid circular imports
    from src.utils.async_llm_manager import cleanup_all_managers
    
    # Clean up all LLM managers
    await cleanup_all_managers()
    
    # Wait for async operations to complete
    await asyncio.sleep(0.3)
    
    # Force garbage collection
    gc.collect()
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited")


@pytest.fixture
async def llm_manager():
    """Fixture to provide AsyncLLMManager with automatic cleanup"""
    from src.utils.llm_factory import create_llm
    from src.utils.async_llm_manager import AsyncLLMManager
    
    llm = create_llm()
    manager = AsyncLLMManager(llm)
    
    try:
        yield manager
    finally:
        await manager.cleanup()