"""Exception classes for the application."""


class CrawlerError(Exception):
    """Base class for crawler exceptions."""
    pass


class ExtractionError(CrawlerError):
    """Raised when data extraction fails."""
    pass


class MaxRetriesExceededError(CrawlerError):
    """Raised when maximum retry attempts are exceeded."""
    pass


class NoValidDataError(CrawlerError):
    """Raised when no valid data could be extracted."""
    pass


class RateLimitError(CrawlerError):
    """Raised when rate limit is exceeded."""
    pass


class URLCollectionError(CrawlerError):
    """Raised when URL collection fails."""
    pass


class LLMError(Exception):
    """Raised when LLM operations fail."""
    pass


class SearchError(Exception):
    """Raised when search operations fail."""
    pass 