"""
Async LLM Manager for proper resource cleanup

This module provides proper async resource management for Google Generative AI
to avoid event loop closure issues during testing.
"""

import asyncio
import contextvars
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


class AsyncLLMManager:
    """Manages async LLM calls with proper cleanup"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self._pending_tasks: set[asyncio.Task] = set()

    async def ainvoke(self, prompt: str, **kwargs: Any) -> BaseMessage:
        """
        Invoke LLM with proper async management
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional arguments for the LLM
            
        Returns:
            The LLM response
        """
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
        """Clean up any pending tasks"""
        if self._pending_tasks:
            # Cancel all pending tasks
            for task in self._pending_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for cancellation to complete
            if self._pending_tasks:
                await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            
            self._pending_tasks.clear()
        
        # Additional wait for gRPC cleanup
        await asyncio.sleep(0.1)


def create_async_llm_manager(llm: BaseChatModel) -> AsyncLLMManager:
    """
    Create an AsyncLLMManager instance
    
    Args:
        llm: The base LLM to wrap
        
    Returns:
        An AsyncLLMManager instance
    """
    return AsyncLLMManager(llm)