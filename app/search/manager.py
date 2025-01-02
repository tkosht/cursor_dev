import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp.client_exceptions import ClientError

from ..exceptions import SearchError

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    score: float


class SearchManager:
    """検索マネージャー

    Google Custom Search APIを使用して検索を実行します。
    環境変数:
        GOOGLE_API_KEY: Google APIキー
        CSE_ID: Custom Search Engine ID
    """

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        self._api_key = os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise SearchError("GOOGLE_API_KEY not found in environment variables")

        self._cse_id = os.getenv("CSE_ID")
        if not self._cse_id:
            raise SearchError("CSE_ID not found in environment variables")

        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリーポイント"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了処理"""
        await self.close()

    async def _ensure_session(self):
        """セッションが存在することを確認"""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )

    async def search(
        self,
        keywords: List[str],
        options: Dict[str, Any]
    ) -> List[SearchResult]:
        """検索の実行

        Args:
            keywords: 検索キーワードのリスト
            options: 検索オプション
                - num: 取得する結果の数（デフォルト: 10）
                - site_restrict: 検索対象サイトの制限
                - date_restrict: 日付による制限

        Returns:
            List[SearchResult]: 検索結果のリスト

        Raises:
            SearchError: 検索に失敗した場合
        """
        if not keywords:
            return []

        query = " OR ".join(keywords)
        try:
            await self._ensure_session()
            results = await self._execute_search(query, options)
            return [
                SearchResult(
                    url=item["link"],
                    title=item["title"],
                    snippet=item.get("snippet", ""),
                    score=self._calculate_relevance(item, keywords)
                )
                for item in results
            ]
        except ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise SearchError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise SearchError(str(e))
        finally:
            if not self._in_context_manager():
                await self.close()

    def _calculate_relevance(
        self,
        item: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """関連性スコアの計算

        Args:
            item: 検索結果アイテム
            keywords: 検索キーワードのリスト

        Returns:
            float: 関連性スコア（0.0 - 1.0）
        """
        if not keywords:
            return 0.0

        text = f"{item['title']} {item.get('snippet', '')}"
        return sum(
            text.lower().count(k.lower()) for k in keywords
        ) / len(keywords)

    def _in_context_manager(self) -> bool:
        """コンテキストマネージャー内で実行されているかを確認"""
        return hasattr(self, '__aexit__')

    async def _execute_search(
        self,
        query: str,
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """検索の実行

        Args:
            query: 検索クエリ
            options: 検索オプション

        Returns:
            List[Dict[str, Any]]: 検索結果のリスト

        Raises:
            SearchError: 検索に失敗した場合
        """
        await self._ensure_session()

        params = {
            "key": self._api_key,
            "cx": self._cse_id,
            "q": query,
            "num": min(options.get("num", 10), 10)  # 最大10件に制限
        }

        # サイト制限の追加
        if site := options.get("site_restrict"):
            params["siteSearch"] = site
            params["siteSearchFilter"] = "i"  # include only

        # 日付制限の追加
        if date := options.get("date_restrict"):
            params["dateRestrict"] = date

        try:
            async with self._session.get(
                self.BASE_URL,
                params=params,
                raise_for_status=True,
                ssl=True  # SSL検証を有効化
            ) as response:
                data = await response.json()
                if "error" in data:
                    error = data["error"]
                    raise SearchError(
                        f"API error: {error.get('message', 'Unknown error')}"
                    )
                return data.get("items", [])

        except ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise SearchError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Search execution failed: {str(e)}")
            raise SearchError(f"Search execution failed: {str(e)}")

    async def close(self):
        """セッションを閉じる"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None 