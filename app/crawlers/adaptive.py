"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
import logging
from typing import Any, Dict, List

from ..exceptions import ExtractionError, MaxRetriesExceededError, NoValidDataError
from ..extraction.manager import ExtractionManager
from ..llm.manager import LLMManager
from ..search.manager import SearchManager

logger = logging.getLogger(__name__)

THRESHOLDS = {
    "relevance": 0.5,
    "validation": 0.8
}

class AdaptiveCrawler:
    def __init__(self, config: Dict[str, Any]):
        self._llm_manager = LLMManager()
        self._search_manager = SearchManager()
        self._extraction_manager = ExtractionManager()
        self._config = config
        self._llm_initialized = False
        self._retry_count = 0
        self._last_error = None

    async def initialize_llm(self) -> None:
        """LLMの初期化を行う"""
        await self._llm_manager.initialize()
        self._llm_initialized = True

    async def crawl_ir_info(
        self,
        company_code: str,
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """IR情報のクローリングを実行"""
        try:
            if not self._llm_initialized:
                await self.initialize_llm()

            while self._retry_count < self._config["max_attempts"]:
                try:
                    keywords = await self._generate_search_keywords(
                        company_code,
                        required_fields
                    )
                    urls = await self._search_urls(keywords)
                    data = await self._extract_data(urls, required_fields)
                    if self._validate_data(data, required_fields):
                        return data
                except Exception as e:
                    self._last_error = e
                    await self._handle_error()
                    self._retry_count += 1

            raise MaxRetriesExceededError()

        except Exception as e:
            logger.error(f"Crawling failed: {str(e)}")
            raise

    async def _generate_search_keywords(
        self,
        company_code: str,
        required_fields: List[str]
    ) -> List[str]:
        """検索キーワードの生成"""
        context = {
            "company_code": company_code,
            "fields": required_fields,
            "attempt": self._retry_count
        }
        return await self._llm_manager.generate_keywords(context)

    async def _search_urls(self, keywords: List[str]) -> List[str]:
        """URLの検索"""
        options = {
            "num": 10,
            "site_restrict": self._config.get("site_restrict"),
            "date_restrict": self._config.get("date_restrict")
        }
        results = await self._search_manager.search(keywords, options)
        return [r.url for r in results if r.score >= THRESHOLDS["relevance"]]

    async def _extract_data(
        self,
        urls: List[str],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """データの抽出"""
        for url in urls:
            try:
                data = await self._extraction_manager.extract(url, required_fields)
                if data.validation_score >= THRESHOLDS["validation"]:
                    return data.data
            except ExtractionError as e:
                logger.warning(f"Extraction failed for {url}: {str(e)}")
                continue
        raise NoValidDataError()

    def _validate_data(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> bool:
        """データの検証"""
        return all(
            field in data and data[field] is not None
            for field in required_fields
        )

    async def _handle_error(self) -> None:
        """エラーハンドリング"""
        delay = min(
            self._config["base_delay"] * (2 ** self._retry_count),
            self._config["max_delay"]
        )
        logger.warning(
            f"Retry {self._retry_count + 1} after {delay}s due to {self._last_error}"
        )
        await asyncio.sleep(delay)
