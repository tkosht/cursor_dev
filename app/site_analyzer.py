"""
サイトアナライザー

Webサイトの内容を分析するクラスを提供します。
"""

import asyncio
import time
from typing import Dict, Optional

import aiohttp
from bs4 import BeautifulSoup

from app.errors.url_analysis_errors import NetworkError, RateLimitError
from app.llm.manager import LLMManager


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
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    async def analyze(self, url: str) -> Dict:
        """URLの内容を分析

        Args:
            url: 分析対象のURL

        Returns:
            分析結果

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        start_time = time.time()

        try:
            content = await self._fetch_content(url)
            text_content = self._extract_text(content)

            llm_start_time = time.time()
            analysis_result = await self.llm_manager.analyze_content(
                text_content, task="url_analysis"
            )
            llm_latency = time.time() - llm_start_time

            processing_time = time.time() - start_time
            return {
                "url": url,
                "analysis": analysis_result,
                "processing_time": processing_time,
                "llm_latency": llm_latency,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "url": url,
                "error": str(e),
                "processing_time": processing_time,
                "llm_latency": 0.0,
            }

    async def _fetch_content(self, url: str) -> str:
        """URLからコンテンツを取得

        Args:
            url: 取得対象のURL

        Returns:
            HTML内容

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
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

    def _extract_text(self, html_content: str) -> str:
        """HTMLからテキストを抽出

        Args:
            html_content: HTML内容

        Returns:
            抽出したテキスト
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # 不要な要素を削除
        for element in soup.find_all(["script", "style", "noscript"]):
            element.decompose()

        # テキストを抽出して整形
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)
