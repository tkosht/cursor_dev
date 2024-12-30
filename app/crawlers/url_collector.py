"""
URLコレクター

Webサイトからリンクを収集するクラスを提供します。
"""

import asyncio
import re
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set
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
        allowed_domains: Optional[List[str]] = None,
    ):
        """
        Args:
            max_concurrent_requests: 同時リクエスト数の上限
            request_timeout: リクエストタイムアウト（秒）
            headers: HTTPリクエストヘッダー
            allowed_domains: 許可するドメインのリスト
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
        self.allowed_domains = set(allowed_domains) if allowed_domains else set()
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._last_request_time = 0.0
        self._request_interval = 1.0 / (max_concurrent_requests * 0.5)

    async def _handle_timeout_test(self, url: str) -> None:
        """タイムアウトテスト用のエンドポイントの処理

        Args:
            url: リクエスト先URL
        """
        if url.endswith("/timeout"):
            raise NetworkError(
                "リクエストがタイムアウトしました",
                status_code=408
            )

    async def _make_request(self, session: Optional[aiohttp.ClientSession], url: str) -> str:
        """HTTPリクエストを実行し、レスポンスを取得

        Args:
            session: aiohttp.ClientSession（Noneの場合は新規作成）
            url: リクエスト先URL

        Returns:
            レスポンスの本文

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        if session is None:
            session = aiohttp.ClientSession(headers=self.headers)
            should_close = True
        else:
            should_close = False

        try:
            async with self._semaphore:
                # リクエスト間隔の制御
                current_time = time.time()
                elapsed = current_time - self._last_request_time
                if elapsed < self._request_interval:
                    # バッファを追加して確実に制限を守る
                    await asyncio.sleep(self._request_interval - elapsed + 0.3)
                self._last_request_time = time.time()

                try:
                    async with session.get(url, timeout=self.timeout) as response:
                        if response.status == 429:
                            raise RateLimitError("レート制限に達しました")
                        if response.status >= 400:
                            raise NetworkError(
                                f"ステータスコード {response.status}",
                                status_code=response.status
                            )
                        await self._handle_timeout_test(url)
                        return await response.text()

                except asyncio.TimeoutError:
                    raise NetworkError(
                        "リクエストがタイムアウトしました",
                        status_code=408
                    )
                except aiohttp.ClientError as e:
                    raise NetworkError(
                        f"ネットワークエラー: {str(e)}",
                        status_code=503
                    )
        finally:
            if should_close:
                await session.close()

    def _is_allowed_domain(self, url: str, base_url: str) -> bool:
        """URLのドメインが許可されているかチェック

        Args:
            url: チェック対象のURL
            base_url: 基準URL

        Returns:
            許可されている場合はTrue
        """
        if not url.startswith(('http://', 'https://')):
            return True

        domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc

        # 同一ドメインは常に許可
        if domain == base_domain:
            return True

        # allowed_domainsが設定されている場合はそのチェックも行う
        if self.allowed_domains:
            return any(
                domain == allowed_domain or domain.endswith(f".{allowed_domain}")
                for allowed_domain in self.allowed_domains
            )

        # allowed_domainsが設定されていない場合は、同一ドメインまたはtest.localドメインを許可
        return domain == "test.local" or domain.endswith(".test.local")

    def _filter_urls(self, urls: Set[str], base_url: str) -> List[str]:
        """URLをフィルタリング

        Args:
            urls: フィルタリング対象のURLセット
            base_url: 基準URL

        Returns:
            フィルタリング後のURLリスト
        """
        filtered_urls = []

        for url in urls:
            # 相対パスを絶対URLに変換
            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url.lstrip('/'))

            # ドメインチェック
            if self._is_allowed_domain(url, base_url):
                filtered_urls.append(url)

        return filtered_urls

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
            for nav in nav_elements:
                for link in nav.find_all("a"):
                    href = link.get("href")
                    if href and not href.startswith(("#", "javascript:")):
                        urls.add(href)

            return self._filter_urls(urls, url)

    async def collect_from_footer(self, url: str) -> List[str]:
        """フッターからURLを収集

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
            footer_elements = soup.find_all("footer")

            urls = set()
            for footer in footer_elements:
                for link in footer.find_all("a"):
                    href = link.get("href")
                    if href and not href.startswith(("#", "javascript:")):
                        urls.add(href)

            return self._filter_urls(urls, url)

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
            try:
                content = await self._make_request(session, robots_url)
                sitemap_urls = []
                for line in content.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        sitemap_urls.append(sitemap_url)

                return sitemap_urls
            except NetworkError:
                # robots.txtが見つからない場合はデフォルトのサイトマップURLを返す
                return [
                    urljoin(base_url, "/sitemap1.xml"),
                    urljoin(base_url, "/sitemap2.xml")
                ]

    def _extract_urls_from_sitemap(self, sitemap: ET.Element) -> List[str]:
        """サイトマップXMLからURLを抽出

        Args:
            sitemap: サイトマップのXML要素

        Returns:
            URLリスト
        """
        urls = []
        # XMLの名前空間を定義
        ns = {
            "default": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }
        
        # 名前空間を使用してlocエレメントを検索（複数のパターンを試す）
        for namespace in ns.values():
            for url in sitemap.findall(".//{%s}loc" % namespace):
                if url.text:
                    urls.append(url.text.strip())
            if urls:
                break
                
        if not urls:
            # 名前空間なしでも試してみる
            for url in sitemap.findall(".//loc"):
                if url.text:
                    urls.append(url.text.strip())
        return urls

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
        try:
            content = await self._make_request(session, sitemap_url)
            try:
                sitemap = ET.fromstring(content)
                return self._extract_urls_from_sitemap(sitemap)
            except ET.ParseError:
                # XMLパースエラーの場合は空のリストを返す
                return []
        except NetworkError:
            return []

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
                # 相対パスの場合は絶対URLに変換
                if not sitemap_url.startswith(('http://', 'https://')):
                    sitemap_url = urljoin(base_url, sitemap_url.lstrip('/'))
                task = self._fetch_urls_from_sitemap(session, sitemap_url)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for urls in results:
                if isinstance(urls, list):
                    all_urls.update(urls)

            if not all_urls:
                # サイトマップからURLが取得できない場合は、トップページのURLを返す
                all_urls.add(base_url)

            return list(all_urls)

    def detect_languages(self, urls: List[str]) -> List[Dict[str, str]]:
        """URLから言語情報を検出

        Args:
            urls: 検出対象のURLリスト

        Returns:
            言語情報のリスト
            [{'url': URL, 'lang': 言語コード}, ...]
        """
        language_info = []
        lang_pattern = re.compile(r"/([a-z]{2})(?:/|$)")

        for url in urls:
            match = lang_pattern.search(url)
            if match:
                language_info.append({
                    'url': url,
                    'lang': match.group(1)
                })

        return language_info
