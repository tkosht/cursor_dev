"""
サイトアナライザー

Webサイトの内容を分析するクラスを提供します。
"""

import asyncio
import logging
import ssl
import time
from typing import Any, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup

from app.errors.url_analysis_errors import NetworkError, RateLimitError
from app.llm.manager import LLMManager

logger = logging.getLogger(__name__)


class URLAnalyzer:
    """URLの内容を分析するクラス"""

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        request_timeout: float = 30.0,
        headers: Optional[dict] = None,
    ):
        """
        Args:
            llm_manager: LLMマネージャー
            request_timeout: リクエストタイムアウト（秒）
            headers: HTTPリクエストヘッダー
        """
        self.llm_manager = llm_manager or LLMManager()
        self.timeout = request_timeout
        chrome_version = "120.0.0.0"
        user_agent = (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
        )
        self.headers = headers or {
            "Host": "",  # This will be set per request
            "User-Agent": user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"'
        }
        self._request_count = 0
        self._last_request_time = 0
        self._cookie_jar = aiohttp.CookieJar(unsafe=True)

    async def _fetch_content(self, url: str) -> str:
        """URLからコンテンツを取得

        Args:
            url: URL

        Returns:
            str: 取得したコンテンツ

        Raises:
            NetworkError: ネットワークエラー
            RateLimitError: レート制限エラー
        """
        # レート制限のチェック
        current_time = time.time()
        if self._request_count >= 3 and current_time - self._last_request_time < 60:
            logger.error(f"Rate limit exceeded for URL: {url}")
            raise RateLimitError("Too many requests")

        try:
            logger.debug(f"Fetching content from URL: {url}")
            # SSLコンテキストの設定
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")

            # ホストヘッダーの設定
            headers = self.headers.copy()
            headers["Host"] = url.split("/")[2]

            conn = aiohttp.TCPConnector(
                ssl=ssl_context,
                force_close=True,
                enable_cleanup_closed=True
            )

            session_kwargs = {
                "cookie_jar": self._cookie_jar,
                "connector": conn,
                "headers": headers,
                "timeout": aiohttp.ClientTimeout(total=self.timeout),
                "trust_env": True
            }

            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.get(url) as response:
                    logger.debug(f"Response status for {url}: {response.status}")
                    if response.status == 429:
                        raise RateLimitError(f"Rate limit exceeded: {response.status}")
                    elif response.status == 403:
                        logger.error(f"Access denied for URL: {url}")
                        raise NetworkError("Access denied", status_code=response.status)
                    elif response.status != 200:
                        logger.error(f"Network error for URL: {url}, status: {response.status}")
                        raise NetworkError(
                            f"Network error for ステータスコード {response.status}",
                            status_code=response.status
                        )

                    content = await response.text()
                    self._request_count += 1
                    self._last_request_time = current_time
                    logger.debug(f"Successfully fetched content from {url}")
                    return content

        except aiohttp.ClientError as e:
            logger.error(f"Network error for URL {url}: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}", status_code=0)
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for URL {url}")
            raise NetworkError("Request timeout", status_code=408)

    async def analyze(self, url: str) -> Dict[str, Any]:
        """URLの内容を分析

        Args:
            url: 分析対象のURL

        Returns:
            Dict[str, Any]: 分析結果
        """
        try:
            logger.debug(f"Starting analysis for URL: {url}")
            content = await self._fetch_content(url)
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()
            llm_response = await self.llm_manager.analyze_content(text[:3000], task="company_info")
            logger.debug(f"Analysis completed for URL: {url}")
            return {
                "llm_response": llm_response
            }
        except (NetworkError, RateLimitError) as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            return {
                "error": str(e),
                "relevance_score": 0.0,
                "category": "error",
                "reason": str(e),
                "confidence": 0.0,
                "processing_time": 0.0,
                "llm_response": {}
            }
