"""
クローラーの基底クラス

全てのクローラーの基底となるクラスを定義します。
"""

import logging
from abc import ABC
from typing import Any, Dict, Optional

import aiohttp
from sqlalchemy.orm import Session

from app.monitoring.monitor import CrawlerMonitor


class BaseCrawler(ABC):
    """
    クローラーの基本クラス

    Attributes:
        session (Session): データベースセッション
        headers (Dict[str, str]): HTTPリクエストヘッダー
        timeout (aiohttp.ClientTimeout): リクエストタイムアウト
        max_retries (int): リトライ回数
        logger (logging.Logger): ロガー
        connector (aiohttp.TCPConnector): HTTP接続用コネクタ
    """

    def __init__(
        self,
        company_code: Optional[str] = None,
        session: Optional[Session] = None,
        monitor: Optional[CrawlerMonitor] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
        connector: Optional[aiohttp.TCPConnector] = None,
        max_retries: int = 3,
    ):
        """
        Args:
            company_code: 企業コード
            session: DBセッション
            monitor: モニタリングインスタンス
            headers: HTTPリクエストヘッダー
            timeout: リクエストタイムアウト
            connector: HTTP接続用コネクタ
            max_retries: リトライ回数
        """
        self.company_code = company_code
        self.session = session
        self.monitor = monitor or CrawlerMonitor()
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.timeout = timeout or aiohttp.ClientTimeout(total=30)
        self.connector = connector or aiohttp.TCPConnector(
            limit=10,
            enable_cleanup_closed=True,
            force_close=False,
            keepalive_timeout=60
        )
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """非同期コンテキストマネージャのエントリーポイント"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                connector=self.connector
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャのクリーンアップ"""
        if self._session:
            await self._session.close()
            self._session = None

    def crawl(self) -> None:
        """クロール処理を実行"""
        try:
            if self.company_code:
                self.monitor.start_crawler(self.company_code)
            self._crawl()
            if self.company_code:
                self.monitor.stop_crawler(self.company_code)
        except Exception as e:
            if self.company_code:
                self.monitor.log_error(self.company_code, e)
                self.monitor.stop_crawler(self.company_code, status="error")
            else:
                self.logger.error(f"クロール処理でエラーが発生: {str(e)}")
            raise

    def _crawl(self) -> None:
        """実際のクロール処理

        サブクラスで実装する必要があります。
        """
        raise NotImplementedError("Subclasses must implement _crawl method")

    def _update_progress(self, crawled_pages: int, total_items: int) -> None:
        """進捗状況を更新

        Args:
            crawled_pages: クロール済みページ数
            total_items: 取得済みアイテム数
        """
        if self.company_code:
            self.monitor.update_progress(self.company_code, crawled_pages, total_items)
        else:
            self.logger.info(f"進捗更新: {crawled_pages}/{total_items}")

    def _log_warning(self, message: str) -> None:
        """警告を記録

        Args:
            message: 警告メッセージ
        """
        if self.company_code:
            self.monitor.log_warning(self.company_code, message)
        else:
            self.logger.warning(message)

    async def _make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> aiohttp.ClientResponse:
        """
        非同期HTTPリクエストの実行

        Args:
            url: リクエスト先URL
            method: HTTPメソッド
            **kwargs: aiohttpライブラリに渡す追加パラメータ

        Returns:
            ClientResponse: レスポンスオブジェクト

        Raises:
            aiohttp.ClientError: リクエスト失敗時
        """
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                connector=self.connector
            )

        for attempt in range(self.max_retries):
            try:
                response = await self._session.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except aiohttp.ClientError as e:
                self._log_warning(
                    f"リクエスト失敗 (試行 {attempt + 1}/{self.max_retries}): {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    raise

        raise aiohttp.ClientError("最大リトライ回数を超過しました")

    def save(self, data: Any) -> None:
        """
        データの保存

        Args:
            data: 保存するデータ
        """
        if self.session is None:
            self.logger.warning("No database session available")
            return

        try:
            self.session.add(data)
            self.session.commit()
            self.logger.info(f"Saved data: {data}")

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Failed to save data: {str(e)}")
            raise

    async def close(self) -> None:
        """リソースのクリーンアップ"""
        if self._session:
            await self._session.close()
            self._session = None
