"""
Unit tests for A2A MVP core exceptions.
Following TDD approach - tests written first.
"""

import pytest


class TestA2AExceptions:
    """Test cases for A2A custom exceptions."""

    def test_a2a_base_exception(self):
        """Test base A2A exception."""
        from app.a2a_mvp.core.exceptions import A2AException

        with pytest.raises(A2AException) as exc_info:
            raise A2AException("Base error occurred")

        assert str(exc_info.value) == "Base error occurred"
        assert exc_info.value.message == "Base error occurred"

    def test_task_not_found_exception(self):
        """Test TaskNotFoundException."""
        from app.a2a_mvp.core.exceptions import TaskNotFoundException

        with pytest.raises(TaskNotFoundException) as exc_info:
            raise TaskNotFoundException("task-123")

        assert "task-123" in str(exc_info.value)
        assert exc_info.value.task_id == "task-123"

    def test_invalid_task_data_exception(self):
        """Test InvalidTaskDataException."""
        from app.a2a_mvp.core.exceptions import InvalidTaskDataException

        with pytest.raises(InvalidTaskDataException) as exc_info:
            raise InvalidTaskDataException("Title is required")

        assert str(exc_info.value) == "Invalid task data: Title is required"
        assert exc_info.value.reason == "Title is required"

    def test_storage_exception(self):
        """Test StorageException."""
        from app.a2a_mvp.core.exceptions import StorageException

        with pytest.raises(StorageException) as exc_info:
            raise StorageException("Database connection failed")

        assert (
            str(exc_info.value) == "Storage error: Database connection failed"
        )

    def test_a2a_protocol_exception(self):
        """Test A2AProtocolException."""
        from app.a2a_mvp.core.exceptions import A2AProtocolException

        with pytest.raises(A2AProtocolException) as exc_info:
            raise A2AProtocolException("Invalid message format")

        assert (
            str(exc_info.value) == "A2A protocol error: Invalid message format"
        )

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from A2AException."""
        from app.a2a_mvp.core.exceptions import (
            A2AException,
            A2AProtocolException,
            InvalidTaskDataException,
            StorageException,
            TaskNotFoundException,
        )

        # All custom exceptions should inherit from A2AException
        assert issubclass(TaskNotFoundException, A2AException)
        assert issubclass(InvalidTaskDataException, A2AException)
        assert issubclass(StorageException, A2AException)
        assert issubclass(A2AProtocolException, A2AException)

        # Test catching with base exception
        with pytest.raises(A2AException):
            raise TaskNotFoundException("task-456")

        with pytest.raises(A2AException):
            raise InvalidTaskDataException("Invalid data")
