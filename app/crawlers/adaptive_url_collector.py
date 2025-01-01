"""Adaptive URL collector implementation."""

import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..exceptions import ExtractionError, URLCollectionError
from ..llm.manager import LLMManager
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class AdaptiveURLCollector(BaseCrawler):
    """Adaptive URL collector that uses LLM for intelligent crawling."""

    def __init__(
        self,
        llm_manager: LLMManager,
        max_concurrent_requests: int = 3,
        request_timeout: float = 30.0,
        max_retries: int = 3,
        allowed_domains: Optional[List[str]] = None
    ):
        """Initialize the adaptive URL collector.

        Args:
            llm_manager: LLM manager for intelligent analysis
            max_concurrent_requests: Maximum number of concurrent requests
            request_timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            allowed_domains: List of allowed domains
        """
        super().__init__(
            max_concurrent_requests=max_concurrent_requests,
            request_timeout=request_timeout,
            max_retries=max_retries
        )
        self.llm_manager = llm_manager
        self.allowed_domains = set(allowed_domains) if allowed_domains else set()
        self.extraction_patterns = {}

    def _is_allowed_domain(self, url: str, base_url: str) -> bool:
        """Check if the URL's domain is allowed.

        Args:
            url: URL to check
            base_url: Base URL for comparison

        Returns:
            True if the domain is allowed
        """
        if not url.startswith(("http://", "https://")):
            return True

        domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc

        if domain == base_domain:
            return True

        if self.allowed_domains:
            return any(
                domain == allowed_domain or domain.endswith(f".{allowed_domain}")
                for allowed_domain in self.allowed_domains
            )

        return False

    def _filter_urls(self, urls: Set[str], base_url: str) -> List[str]:
        """Filter URLs based on domain and convert relative paths.

        Args:
            urls: Set of URLs to filter
            base_url: Base URL for resolving relative paths

        Returns:
            List of filtered URLs
        """
        filtered_urls = []

        for url in urls:
            if not url.startswith(("http://", "https://")):
                url = urljoin(base_url, url.lstrip("/"))

            if self._is_allowed_domain(url, base_url):
                filtered_urls.append(url)

        return sorted(filtered_urls)

    async def analyze_page_structure(
        self,
        html: str,
        url: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze page structure using LLM.

        Args:
            html: HTML content to analyze
            url: URL of the page
            context: Additional context for analysis

        Returns:
            Analysis results including extraction patterns
        """
        try:
            analysis_context = {
                "url": url,
                "previous_patterns": self.extraction_patterns,
                **(context or {})
            }
            
            soup = BeautifulSoup(html, "html.parser")
            analysis_context["page_structure"] = {
                "title": soup.title.string if soup.title else None,
                "main_content": bool(soup.find("main")),
                "navigation": bool(soup.find(["nav", "header"])),
                "footer": bool(soup.find("footer"))
            }

            analysis = await self.llm_manager.analyze_structure(analysis_context)
            
            if "patterns" in analysis:
                self.extraction_patterns.update(analysis["patterns"])
            
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze page structure: {e}")
            raise ExtractionError(f"Page structure analysis failed: {e}")

    async def _extract_urls_with_strategy(
        self,
        html: str,
        analysis: Dict[str, Any]
    ) -> Set[str]:
        """Extract URLs using the analysis-based strategy.

        Args:
            html: HTML content to extract from
            analysis: Analysis results from LLM

        Returns:
            Set of extracted URLs
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            urls = set()

            for pattern in analysis.get("patterns", []):
                if "selector" in pattern:
                    elements = soup.select(pattern["selector"])
                    for element in elements:
                        if pattern.get("type") == "link":
                            href = element.get("href")
                            if href and not href.startswith(("#", "javascript:")):
                                urls.add(href)
                        elif pattern.get("type") == "text":
                            text = element.get_text(strip=True)
                            if text:
                                # URLを抽出するための追加処理
                                pass

            return urls

        except Exception as e:
            logger.error(f"Failed to extract URLs with strategy: {e}")
            raise ExtractionError(f"URL extraction failed: {e}")

    async def collect_urls_adaptively(
        self,
        url: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Collect URLs using adaptive strategy.

        Args:
            url: Target page URL
            context: Additional context for collection

        Returns:
            List of collected URLs

        Raises:
            URLCollectionError: If URL collection fails
        """
        try:
            html = await self.get_page(url)
            analysis = await self.analyze_page_structure(html, url, context)
            urls = await self._extract_urls_with_strategy(html, analysis)
            
            # フィードバックを収集
            self._update_extraction_patterns(analysis, len(urls))
            
            return self._filter_urls(urls, url)

        except Exception as e:
            logger.error(f"Failed to collect URLs adaptively: {e}")
            raise URLCollectionError(f"Adaptive URL collection failed: {e}")

    def _update_extraction_patterns(
        self,
        analysis: Dict[str, Any],
        num_urls: int
    ) -> None:
        """Update extraction patterns based on results.

        Args:
            analysis: Analysis results
            num_urls: Number of URLs collected
        """
        if num_urls > 0 and "patterns" in analysis:
            for pattern in analysis["patterns"]:
                if "selector" in pattern:
                    self.extraction_patterns[pattern["selector"]] = {
                        "success_count": self.extraction_patterns.get(
                            pattern["selector"], {}
                        ).get("success_count", 0) + 1,
                        "last_used": pattern
                    } 