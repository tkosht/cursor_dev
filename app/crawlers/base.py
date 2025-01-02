"""Base crawler implementation."""

import asyncio
import logging
from typing import Optional

import aiohttp

from ..exceptions import URLCollectionError

logger = logging.getLogger(__name__)


class BaseCrawler:
    """Base crawler class."""

    def __init__(
        self,
        max_concurrent_requests: int = 3,
        request_timeout: float = 30.0,
        max_retries: int = 3
    ):
        """Initialize the crawler.

        Args:
            max_concurrent_requests: Maximum number of concurrent requests
            request_timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリーポイント"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了処理"""
        if self._session:
            await self._session.close()
            self._session = None

    async def get_page(self, url: str) -> Optional[str]:
        """ページを取得

        Args:
            url: 取得対象のURL

        Returns:
            Optional[str]: 取得したページのHTML

        Raises:
            URLCollectionError: ページの取得に失敗した場合
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._semaphore:
                async with self._session.get(
                    url,
                    timeout=self.request_timeout
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise URLCollectionError(
                            f"ステータスコード {response.status}: {url}"
                        )

        except asyncio.TimeoutError:
            raise URLCollectionError(f"タイムアウト: {url}")
        except Exception as e:
            raise URLCollectionError(f"ページ取得中にエラー: {str(e)}")

    async def close(self):
        """セッションを閉じる"""
        if self._session:
            await self._session.close()
            self._session = None
