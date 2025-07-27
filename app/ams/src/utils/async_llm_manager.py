"""
Async LLM Manager for proper resource cleanup

This module provides proper async resource management for Google Generative AI
to avoid event loop closure issues during testing.
"""

import asyncio
import gc
import weakref
from typing import Any, Optional, Set

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


# Global registry of all active managers for cleanup
_active_managers: Set[weakref.ref] = set()


class AsyncLLMManager:
    """Manages async LLM calls with proper cleanup"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self._pending_tasks: set[asyncio.Task] = set()
        self._closed = False
        # Register this manager globally
        _active_managers.add(weakref.ref(self, lambda ref: _active_managers.discard(ref)))

    async def ainvoke(self, prompt: str, **kwargs: Any) -> BaseMessage:
        """
        Invoke LLM with proper async management
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional arguments for the LLM
            
        Returns:
            The LLM response
        """
        if self._closed:
            raise RuntimeError("AsyncLLMManager is closed")
            
        # Create task and track it
        task = asyncio.create_task(self._do_invoke(prompt, **kwargs))
        self._pending_tasks.add(task)
        
        try:
            result = await task
            return result
        finally:
            # Remove completed task
            self._pending_tasks.discard(task)

    async def _do_invoke(self, prompt: str, **kwargs: Any) -> BaseMessage:
        """Actually invoke the LLM"""
        try:
            return await self.llm.ainvoke(prompt, **kwargs)
        except Exception as e:
            # Ensure proper cleanup even on error
            await asyncio.sleep(0)  # Yield to event loop
            raise

    async def cleanup(self) -> None:
        """Clean up any pending tasks and close the manager"""
        if self._closed:
            return
            
        self._closed = True
        
        # Cancel all pending tasks
        if self._pending_tasks:
            for task in list(self._pending_tasks):
                if not task.done():
                    task.cancel()
            
            # Wait for cancellation to complete
            if self._pending_tasks:
                await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            
            self._pending_tasks.clear()
        
        # Force cleanup of gRPC resources
        if hasattr(self.llm, '_client'):
            # For Google Generative AI
            client = getattr(self.llm, '_client', None)
            if client and hasattr(client, 'close'):
                try:
                    await asyncio.sleep(0.1)  # Give time for pending operations
                    # Note: close() might not be async, handle both cases
                    if asyncio.iscoroutinefunction(client.close):
                        await client.close()
                    else:
                        client.close()
                except Exception:
                    pass  # Ignore cleanup errors
        
        # Additional wait for gRPC cleanup
        await asyncio.sleep(0.2)
        
        # Force garbage collection
        gc.collect()

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        await self.cleanup()


async def cleanup_all_managers():
    """Clean up all active managers globally"""
    # Create a list to avoid modification during iteration
    managers = []
    for ref in list(_active_managers):
        manager = ref()
        if manager:
            managers.append(manager)
    
    # Clean up all managers
    if managers:
        await asyncio.gather(
            *[manager.cleanup() for manager in managers],
            return_exceptions=True
        )
    
    _active_managers.clear()


def create_async_llm_manager(llm: BaseChatModel) -> AsyncLLMManager:
    """
    Create an AsyncLLMManager instance
    
    Args:
        llm: The base LLM to wrap
        
    Returns:
        An AsyncLLMManager instance
    """
    return AsyncLLMManager(llm)