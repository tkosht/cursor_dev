"""Exception classes for the application."""


class BaseError(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class CrawlerError(BaseError):
    """Base class for crawler exceptions."""
    pass


class ExtractionError(CrawlerError):
    """Raised when data extraction fails."""
    pass


class MaxRetriesExceededError(CrawlerError):
    """Raised when maximum retry attempts are exceeded."""
    pass


class RateLimitError(CrawlerError):
    """Raised when rate limit is exceeded."""
    pass


class URLCollectionError(CrawlerError):
    """Raised when URL collection fails."""
    pass


class NoValidDataError(CrawlerError):
    """Raised when no valid data could be extracted."""
    pass


class LLMError(BaseError):
    """Base class for LLM related errors."""
    pass


class ModelNotFoundError(LLMError):
    """Raised when model is not found."""
    pass


class SearchError(BaseError):
    """Raised when search operations fail."""
    pass


class TooFrequentAccessError(CrawlerError):
    """アクセス間隔が短すぎる場合の例外"""
    pass


class NoValidURLError(Exception):
    """有効なURLが見つからない場合に発生する例外。"""
    pass 