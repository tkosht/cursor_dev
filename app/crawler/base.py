"""
基本クローラー

このモジュールは、クローラーの基本機能を提供します。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from app.models import get_session


class BaseCrawler(ABC):
    """
    クローラーの基本クラス

    すべてのクローラーはこのクラスを継承して実装します。

    Attributes:
        session (Session): データベースセッション
        headers (Dict[str, str]): HTTPリクエストヘッダー
        timeout (int): リクエストタイムアウト（秒）
        max_retries (int): リトライ回数
        logger (logging.Logger): ロガー
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        クローラーを初期化します。

        Args:
            session (Optional[Session]): データベースセッション
            headers (Optional[Dict[str, str]]): HTTPリクエストヘッダー
            timeout (int): リクエストタイムアウト（秒）
            max_retries (int): リトライ回数
        """
        self.session = session or get_session()
        self.headers = headers or {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)

    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Optional[requests.Response]:
        """
        HTTPリクエストを実行します。

        Args:
            url (str): リクエストURL
            method (str): HTTPメソッド
            params (Optional[Dict[str, Any]]): クエリパラメータ
            data (Optional[Dict[str, Any]]): リクエストボディ
            retry_count (int): 現在のリトライ回数

        Returns:
            Optional[requests.Response]: レスポンス。エラー時はNone

        Raises:
            RequestException: リトライ回数を超えてもリクエストが失敗した場合
        """
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response

        except RequestException as e:
            self.logger.warning(f"Request failed: {str(e)}")
            if retry_count < self.max_retries:
                self.logger.info(f"Retrying... ({retry_count + 1}/{self.max_retries})")
                return self._make_request(url, method, params, data, retry_count + 1)
            else:
                self.logger.error(f"Max retries exceeded for URL: {url}")
                raise

    @abstractmethod
    def crawl(self) -> None:
        """
        クローリングを実行します。
        このメソッドは各クローラーで実装する必要があります。
        """
        pass

    def save(self, data: Any) -> None:
        """
        データを保存します。
        必要に応じてサブクラスでオーバーライドできます。

        Args:
            data (Any): 保存するデータ
        """
        try:
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Failed to save data: {str(e)}")
            self.session.rollback()
            raise
