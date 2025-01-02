"""アクセス制御の実装"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlparse

from ..exceptions import TooFrequentAccessError

logger = logging.getLogger(__name__)


class AccessController:
    """アクセス制御を管理するクラス"""

    def __init__(
        self,
        max_concurrent: int = 5,
        min_interval: int = 3600,
        domain_interval: int = 60
    ):
        """初期化

        Args:
            max_concurrent: 最大同時接続数
            min_interval: URL単位の最小アクセス間隔（秒）
            domain_interval: ドメイン単位の最小アクセス間隔（秒）
        """
        self._url_access_times: Dict[str, datetime] = {}
        self._domain_access_times: Dict[str, datetime] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._min_interval = min_interval
        self._domain_interval = domain_interval

    async def acquire(self, url: str) -> None:
        """アクセス権を取得

        Args:
            url: アクセス対象のURL

        Raises:
            TooFrequentAccessError: アクセス間隔が短すぎる場合
        """
        domain = self._extract_domain(url)
        await self._check_domain_access(domain)
        await self._check_url_access(url)
        await self._semaphore.acquire()

        # アクセス時刻を記録
        now = datetime.now()
        self._url_access_times[url] = now
        self._domain_access_times[domain] = now

    def release(self) -> None:
        """アクセス権を解放"""
        self._semaphore.release()

    async def _check_domain_access(self, domain: str) -> None:
        """ドメインごとのアクセス制御をチェック

        Args:
            domain: チェック対象のドメイン

        Raises:
            TooFrequentAccessError: アクセス間隔が短すぎる場合
        """
        last_time = self._domain_access_times.get(domain)
        if last_time:
            elapsed = datetime.now() - last_time
            if elapsed < timedelta(seconds=self._domain_interval):
                wait_time = self._domain_interval - elapsed.seconds
                logger.warning(
                    f"ドメイン {domain} へのアクセスが頻繁すぎます。"
                    f"{wait_time}秒待機します。"
                )
                await asyncio.sleep(wait_time)

    async def _check_url_access(self, url: str) -> None:
        """URL単位のアクセス制御をチェック

        Args:
            url: チェック対象のURL

        Raises:
            TooFrequentAccessError: アクセス間隔が短すぎる場合
        """
        last_time = self._url_access_times.get(url)
        if last_time:
            elapsed = datetime.now() - last_time
            if elapsed < timedelta(seconds=self._min_interval):
                wait_time = self._min_interval - elapsed.seconds
                logger.warning(
                    f"URL {url} へのアクセスが頻繁すぎます。"
                    f"{wait_time}秒待機します。"
                )
                await asyncio.sleep(wait_time)

    @staticmethod
    def _extract_domain(url: str) -> str:
        """URLからドメインを抽出

        Args:
            url: 対象のURL

        Returns:
            str: 抽出したドメイン
        """
        parsed = urlparse(url)
        return parsed.netloc 