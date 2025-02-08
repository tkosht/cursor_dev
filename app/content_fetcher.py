"""コンテンツを取得するモジュール。"""

import logging
from typing import Dict
from urllib.parse import urlparse

import requests

from app.exceptions import ContentFetchError
from app.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class ContentFetcher:
    """コンテンツを取得するクラス。"""

    def __init__(self):
        """初期化。"""
        self._monitor = PerformanceMonitor()

    def fetch_content(self, url: str) -> str:
        """URLからコンテンツを取得する。

        Args:
            url: 取得対象のURL

        Returns:
            str: 取得したHTMLコンテンツ

        Raises:
            ValueError: URLが不正な場合
            ContentFetchError: コンテンツの取得に失敗した場合
        """
        try:
            self._validate_url(url)
            self._monitor.start_operation('fetch_content')

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            self._monitor.end_operation('fetch_content', True)
            return response.text

        except requests.Timeout as e:
            self._monitor.end_operation('fetch_content', False, error='timeout')
            logger.error(f"タイムアウトが発生しました: {str(e)}")
            raise ContentFetchError(f"タイムアウトが発生しました: {str(e)}")

        except requests.RequestException as e:
            self._monitor.end_operation('fetch_content', False, error='request_error')
            logger.error(f"リクエストエラーが発生しました: {str(e)}")
            raise ContentFetchError(f"リクエストエラーが発生しました: {str(e)}")

        except Exception as e:
            self._monitor.end_operation('fetch_content', False, error='unknown')
            logger.error(f"予期せぬエラーが発生しました: {str(e)}")
            raise ContentFetchError(f"予期せぬエラーが発生しました: {str(e)}")

    def _validate_url(self, url: str) -> None:
        """URLを検証する。

        Args:
            url: 検証対象のURL

        Raises:
            ValueError: URLが不正な場合
        """
        if not url:
            raise ValueError("URLが空です")

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("URLの形式が不正です")
            if result.scheme not in ['http', 'https']:
                raise ValueError("HTTPSプロトコルのみサポートしています")
        except Exception as e:
            raise ValueError(f"URLの解析に失敗しました: {str(e)}")

    def get_metrics(self) -> Dict[str, any]:
        """メトリクスを取得する。

        Returns:
            Dict[str, any]: メトリクス
        """
        return self._monitor.get_metrics() 