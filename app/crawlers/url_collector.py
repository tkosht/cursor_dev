"""
URLコレクター

Webサイトからリンクを収集するクラスを提供します。
"""

import asyncio
import xml.etree.ElementTree as ET
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from app.errors.url_analysis_errors import NetworkError, RateLimitError


class URLCollector:
    """URLを収集するクラス"""

    def __init__(
        self,
        max_concurrent_requests: int = 3,
        request_timeout: float = 30.0,
        headers: Optional[dict] = None,
    ):
        """
        Args:
            max_concurrent_requests: 同時リクエスト数の上限
            request_timeout: リクエストタイムアウト（秒）
            headers: HTTPリクエストヘッダー
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = request_timeout
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> str:
        """HTTPリクエストを実行し、レスポンスを取得

        Args:
            session: aiohttp.ClientSession
            url: リクエスト先URL

        Returns:
            レスポンスの本文

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        async with self._semaphore:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 429:
                        raise RateLimitError("レート制限に達しました")
                    if response.status != 200:
                        raise NetworkError(
                            f"ステータスコード {response.status}", status_code=response.status
                        )
                    return await response.text()

            except asyncio.TimeoutError:
                raise NetworkError("リクエストがタイムアウトしました")
            except aiohttp.ClientError as e:
                raise NetworkError(f"ネットワークエラー: {str(e)}")

    async def collect_from_navigation(self, url: str) -> List[str]:
        """ナビゲーションメニューからURLを収集

        Args:
            url: 対象ページのURL

        Returns:
            収集したURL一覧

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        async with aiohttp.ClientSession(
            headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            content = await self._make_request(session, url)
            soup = BeautifulSoup(content, "html.parser")
            nav_elements = soup.find_all(["nav", "header", "menu"])

            urls = set()
            base_domain = urlparse(url).netloc
            for nav in nav_elements:
                for link in nav.find_all("a"):
                    href = link.get("href")
                    if href and not href.startswith(("#", "javascript:")):
                        full_url = urljoin(url, href)
                        if urlparse(full_url).netloc == base_domain:
                            urls.add(full_url)

            return list(urls)

    async def get_sitemaps_from_robots(self, base_url: str) -> List[str]:
        """robots.txtからサイトマップURLを取得

        Args:
            base_url: 基準URL

        Returns:
            サイトマップURL一覧

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        robots_url = urljoin(base_url, "/robots.txt")

        async with aiohttp.ClientSession(
            headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            content = await self._make_request(session, robots_url)
            sitemap_urls = []
            for line in content.split("\n"):
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    sitemap_urls.append(sitemap_url)

            return sitemap_urls or [urljoin(base_url, "/sitemap.xml")]

    async def _fetch_urls_from_sitemap(
        self, session: aiohttp.ClientSession, sitemap_url: str
    ) -> List[str]:
        """サイトマップからURLを取得

        Args:
            session: aiohttp.ClientSession
            sitemap_url: サイトマップのURL

        Returns:
            URLリスト

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        content = await self._make_request(session, sitemap_url)
        urls = []
        try:
            sitemap = ET.fromstring(content)
            for url in sitemap.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            ):
                urls.append(url.text)
        except ET.ParseError:
            pass
        return urls

    async def collect_from_sitemap(self, base_url: str) -> List[str]:
        """サイトマップからURLを収集

        Args:
            base_url: 基準URL

        Returns:
            収集したURL一覧

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        sitemap_urls = await self.get_sitemaps_from_robots(base_url)
        all_urls = set()

        async with aiohttp.ClientSession(
            headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            tasks = []
            for sitemap_url in sitemap_urls:
                task = self._fetch_urls_from_sitemap(session, sitemap_url)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for urls in results:
                if isinstance(urls, Exception):
                    continue
                all_urls.update(urls)

        return list(all_urls)
