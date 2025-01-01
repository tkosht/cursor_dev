"""Base crawler implementation."""

import asyncio
import logging
from typing import Dict, List, Optional, Set

import httpx
from bs4 import BeautifulSoup

from ..exceptions import (
    CrawlerError,
    ExtractionError,
    MaxRetriesExceededError,
    RateLimitError,
    URLCollectionError,
)
from ..monitoring.monitor import Monitor

logger = logging.getLogger(__name__)


class BaseCrawler:
    """Base class for crawlers."""

    def __init__(
        self,
        max_concurrent_requests: int = 3,
        request_timeout: float = 30.0,
        max_retries: int = 3,
        monitor: Optional[Monitor] = None
    ):
        """Initialize the crawler.

        Args:
            max_concurrent_requests: Maximum number of concurrent requests.
            request_timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            monitor: Optional monitor for tracking crawler metrics.
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.monitor = monitor or Monitor()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def get_page(self, url: str) -> str:
        """Get a page from a URL with retry logic.

        Args:
            url: The URL to fetch.

        Returns:
            The page content.

        Raises:
            MaxRetriesExceededError: If maximum retry attempts are exceeded.
            RateLimitError: If rate limit is exceeded.
            CrawlerError: For other crawler errors.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                async with self.semaphore:
                    async with httpx.AsyncClient() as client:
                        start_time = asyncio.get_event_loop().time()
                        response = await client.get(
                            url,
                            timeout=self.request_timeout,
                            follow_redirects=True
                        )
                        response_time = asyncio.get_event_loop().time() - start_time

                        self.monitor.record_request(
                            success=response.status_code == 200,
                            response_time=response_time
                        )

                        if response.status_code == 429:
                            raise RateLimitError(f"Rate limit exceeded for {url}")
                        response.raise_for_status()
                        return response.text

            except httpx.HTTPError as e:
                retries += 1
                if retries > self.max_retries:
                    raise MaxRetriesExceededError(
                        f"Maximum retries exceeded for {url}: {e}"
                    )
                await asyncio.sleep(2 ** retries)  # Exponential backoff

            except Exception as e:
                raise CrawlerError(f"Failed to fetch {url}: {e}")

    async def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract links from HTML content.

        Args:
            html: The HTML content.
            base_url: The base URL for resolving relative links.

        Returns:
            Set of extracted URLs.

        Raises:
            ExtractionError: If link extraction fails.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = set()

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if href.startswith(("http://", "https://")):
                    links.add(href)
                elif href.startswith("/"):
                    links.add(f"{base_url.rstrip('/')}{href}")

            return links

        except Exception as e:
            raise ExtractionError(f"Failed to extract links: {e}")

    async def collect_urls(self, start_url: str) -> List[str]:
        """Collect URLs from a starting point.

        Args:
            start_url: The URL to start from.

        Returns:
            List of collected URLs.

        Raises:
            URLCollectionError: If URL collection fails.
        """
        try:
            html = await self.get_page(start_url)
            links = await self.extract_links(html, start_url)
            return sorted(list(links))

        except Exception as e:
            raise URLCollectionError(f"Failed to collect URLs from {start_url}: {e}")

    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get crawler metrics.

        Returns:
            Dictionary containing crawler metrics.
        """
        return self.monitor.get_metrics()
