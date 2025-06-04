"""
Custom exceptions for A2A MVP.
"""


class A2AException(Exception):
    """Base exception for all A2A-related errors."""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)


class TaskNotFoundException(A2AException):
    """Raised when a task is not found."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class InvalidTaskDataException(A2AException):
    """Raised when task data is invalid."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid task data: {reason}")


class StorageException(A2AException):
    """Raised when storage operations fail."""

    def __init__(self, message: str):
        super().__init__(f"Storage error: {message}")


class A2AProtocolException(A2AException):
    """Raised when A2A protocol errors occur."""

    def __init__(self, message: str):
        super().__init__(f"A2A protocol error: {message}")
