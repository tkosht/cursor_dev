"""Adaptive URL collector for crawling."""

import logging
import re
from typing import List, Optional, Pattern, Set

from ..exceptions import NoValidDataError
from ..llm.constants import LLMConstants
from ..llm.manager import LLMManager
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class AdaptiveURLCollector(BaseCrawler):
    """Adaptive URL collector for crawling."""

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        max_concurrent_requests: int = 3,
        request_timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        allowed_domains: Optional[List[str]] = None
    ):
        """Initialize the collector.

        Args:
            llm_manager: LLM manager instance
            max_concurrent_requests: Maximum number of concurrent requests
            request_timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            allowed_domains: List of allowed domains to crawl
        """
        super().__init__(
            max_concurrent_requests=max_concurrent_requests,
            request_timeout=request_timeout,
            max_retries=max_retries
        )
        self.llm_manager = llm_manager or LLMManager()
        self.allowed_domains = set(allowed_domains) if allowed_domains else set()
        self.retry_delay = retry_delay
        self._url_pattern: Pattern = re.compile(LLMConstants.URL_PATTERN)

    async def collect_urls(
        self,
        start_url: str,
        max_depth: int = 2,
        max_urls: int = 10
    ) -> Set[str]:
        """Collect URLs from a starting point.

        Args:
            start_url: Starting URL
            max_depth: Maximum depth to crawl
            max_urls: Maximum number of URLs to collect

        Returns:
            Set of collected URLs

        Raises:
            NoValidDataError: If no valid URLs could be collected
        """
        try:
            # 初期URLの検証
            if not self._is_valid_url(start_url):
                raise NoValidDataError(f"無効なURL: {start_url}")

            # URLの収集
            collected_urls = await self._collect_urls_recursive(
                start_url=start_url,
                max_depth=max_depth,
                max_urls=max_urls
            )

            # 結果の検証
            if not collected_urls:
                raise NoValidDataError("URLを収集できませんでした")

            return collected_urls

        except NoValidDataError:
            raise

        except Exception as e:
            logger.error(f"URL収集中にエラー: {e}")
            raise NoValidDataError(f"URL収集中にエラーが発生しました: {e}")

    async def _collect_urls_recursive(
        self,
        start_url: str,
        max_depth: int,
        max_urls: int,
        current_depth: int = 0,
        collected_urls: Optional[Set[str]] = None
    ) -> Set[str]:
        """Recursively collect URLs.

        Args:
            start_url: Starting URL
            max_depth: Maximum depth to crawl
            max_urls: Maximum number of URLs to collect
            current_depth: Current crawling depth
            collected_urls: Set of already collected URLs

        Returns:
            Set of collected URLs
        """
        if collected_urls is None:
            collected_urls = set()

        if current_depth >= max_depth or len(collected_urls) >= max_urls:
            return collected_urls

        try:
            # ページを取得
            content = await self._fetch_page(start_url)
            if not content:
                logger.warning(f"ページ取得に失敗: {start_url}")
                return collected_urls

            # URLを抽出
            page_urls = await self._extract_urls(content, start_url)
            if not page_urls:
                logger.warning(f"URLが見つかりませんでした: {start_url}")
                return collected_urls

            # URLを追加
            collected_urls.update(page_urls)
            if len(collected_urls) >= max_urls:
                return collected_urls

            # 再帰的に収集
            for url in page_urls - collected_urls:
                if len(collected_urls) >= max_urls:
                    break
                await self._collect_urls_recursive(
                    start_url=url,
                    max_depth=max_depth,
                    max_urls=max_urls,
                    current_depth=current_depth + 1,
                    collected_urls=collected_urls
                )

            return collected_urls

        except Exception as e:
            logger.error(f"再帰的URL収集中にエラー: {e}")
            return collected_urls

    async def _extract_urls(self, content: str, base_url: str) -> Set[str]:
        """Extract URLs from content.

        Args:
            content: HTML content
            base_url: Base URL for resolving relative URLs

        Returns:
            Set of extracted URLs
        """
        try:
            # URLを抽出
            urls = set(self._url_pattern.findall(content))
            if not urls:
                return set()

            # URLをフィルタリング
            filtered_urls = set()
            for url in urls:
                if self._is_valid_url(url) and self._is_allowed_domain(url):
                    filtered_urls.add(url)

            return filtered_urls

        except Exception as e:
            logger.error(f"URL抽出中にエラー: {e}")
            return set()

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid.

        Args:
            url: URL to check

        Returns:
            bool: Whether URL is valid
        """
        try:
            return bool(self._url_pattern.match(url))
        except Exception as e:
            logger.error(f"URL検証中にエラー: {e}")
            return False

    def _is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is allowed.

        Args:
            url: URL to check

        Returns:
            bool: Whether domain is allowed
        """
        try:
            if not self.allowed_domains:
                return True

            for domain in self.allowed_domains:
                if domain in url:
                    return True

            return False

        except Exception as e:
            logger.error(f"ドメイン検証中にエラー: {e}")
            return False 