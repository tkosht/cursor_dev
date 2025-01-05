"""HTMLコンテンツを取得するためのモジュール。"""

import logging
from typing import Optional
import requests
from requests.exceptions import RequestException
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentFetcher:
    """HTMLコンテンツを取得するクラス"""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """
        Args:
            timeout (float, optional): リクエストのタイムアウト時間（秒）. デフォルトは30秒
            max_retries (int, optional): リトライ回数. デフォルトは3回
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

    def fetch_html(self, url: str) -> str:
        """指定されたURLからHTMLコンテンツを取得

        Args:
            url (str): 取得対象のURL

        Returns:
            str: 取得したHTMLコンテンツ

        Raises:
            ValueError: URLが空の場合
            ConnectionError: HTTPエラーが発生した場合
            TimeoutError: タイムアウトが発生した場合
        """
        if not url:
            raise ValueError("URL must not be empty")

        try:
            response = self._session.get(url, timeout=self._timeout)
            if not self._verify_response(response):
                raise ConnectionError(f"HTTP error: {response.status_code}")
            return response.text

        except requests.Timeout:
            raise TimeoutError("Request timed out")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch content: {str(e)}")

    def fetch_from_file(self, file_path: str) -> str:
        """指定されたファイルからHTMLコンテンツを読み込み

        Args:
            file_path (str): 読み込むファイルのパス

        Returns:
            str: 読み込んだHTMLコンテンツ

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            IOError: ファイルの読み込みに失敗した場合
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Failed to read file: {str(e)}")

    def _verify_response(self, response: requests.Response) -> bool:
        """HTTPレスポンスが正常かどうかを確認

        Args:
            response (requests.Response): 確認対象のレスポンス

        Returns:
            bool: 正常な場合はTrue、それ以外はFalse
        """
        return 200 <= response.status_code < 300 