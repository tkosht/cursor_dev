"""Base crawler module."""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Type

from playwright.sync_api import Browser, Page, sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Base crawler class for web scraping."""

    def __init__(
        self,
        base_url: str,
        storage_dir: Optional[Path] = None,
        headless: bool = True,
    ) -> None:
        """Initialize the crawler.

        Args:
            base_url: Base URL for crawling
            storage_dir: Directory to store downloaded files
            headless: Whether to run browser in headless mode
        """
        self.base_url = base_url
        self.storage_dir = storage_dir or Path("data")
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._setup_storage()

    def _setup_storage(self) -> None:
        """Setup storage directory."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        """Start the browser session."""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

    def stop(self) -> None:
        """Stop the browser session."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()

    def __enter__(self) -> 'BaseCrawler':
        """Context manager entry."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> None:
        """Context manager exit.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.stop()

    @abstractmethod
    def crawl(self) -> Dict[str, Any]:
        """Crawl the website and return extracted data.

        Returns:
            Dictionary containing extracted data
        """
        pass
