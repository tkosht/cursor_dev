"""Adaptive crawler for collecting IR information."""

import logging
from typing import Any, Dict, List, Optional

from ..extraction.manager import ExtractionManager
from ..llm.manager import LLMManager
from ..search.manager import SearchManager
from ..validation.field_validator import FieldValidator
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class AdaptiveCrawler(BaseCrawler):
    """IR情報を収集するアダプティブクローラー"""

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        search_manager: Optional[SearchManager] = None,
        extraction_manager: Optional[ExtractionManager] = None,
        field_validator: Optional[FieldValidator] = None
    ):
        """クローラーを初期化する。

        Args:
            llm_manager: LLMマネージャー
            search_manager: 検索マネージャー
            extraction_manager: 抽出マネージャー
            field_validator: フィールドバリデーター
        """
        super().__init__()
        self._llm_manager = llm_manager or LLMManager()
        self._search_manager = search_manager or SearchManager()
        self._extraction_manager = extraction_manager or ExtractionManager()
        self._field_validator = field_validator or FieldValidator()

    async def crawl_ir_info(
        self,
        company_code: str,
        target_fields: List[str]
    ) -> Optional[Dict[str, Any]]:
        """IR情報をクロールして収集する。

        Args:
            company_code (str): 企業コード
            target_fields (List[str]): 収集対象のフィールド

        Returns:
            Optional[Dict[str, Any]]: 収集されたデータ。失敗時はNone。
        """
        try:
            # 検索キーワードを生成
            keywords = await self._llm_manager.generate_search_keywords(
                company_code,
                target_fields
            )
            if not keywords:
                logger.warning(f"Failed to generate search keywords for: {company_code}")
                return None

            # URLを検索
            urls = await self._search_urls(keywords)
            if not urls:
                logger.warning(f"No URLs found for: {company_code}")
                return None

            # 各URLからデータを収集
            collected_data = None
            for url in urls:
                data = await self._collect_from_url(url, target_fields)
                if data:
                    collected_data = data
                    break

            if not collected_data:
                logger.warning(f"No valid data collected for: {company_code}")
                return None

            return collected_data

        except Exception as e:
            logger.error(f"Crawling failed for {company_code}: {e}")
            return None

    async def _search_urls(self, keywords: List[str]) -> List[str]:
        """キーワードを使用してURLを検索する。

        Args:
            keywords (List[str]): 検索キーワードのリスト

        Returns:
            List[str]: 検索結果のURLリスト
        """
        search_options = {
            "num": 10,  # 検索結果の最大数
            "date_restrict": "m6",  # 過去6ヶ月以内の結果に制限
            "safe": "active",  # セーフサーチを有効化
        }

        urls = []
        for keyword in keywords:
            try:
                results = await self._search_manager.search(
                    keyword,
                    options=search_options
                )
                if results:
                    urls.extend(results)
            except Exception as e:
                logger.error(f"Search failed for keyword '{keyword}': {e}")
                continue

        return list(set(urls))  # 重複を除去

    async def _collect_from_url(
        self,
        url: str,
        target_fields: List[str]
    ) -> Optional[Dict[str, Any]]:
        """指定されたURLからデータを収集する。

        Args:
            url (str): 収集対象のURL
            target_fields (List[str]): 収集対象のフィールド

        Returns:
            Optional[Dict[str, Any]]: 収集されたデータ。失敗時はNone。
        """
        try:
            # ページを取得
            content = await self._fetch_page(url)
            if not content:
                logger.warning(f"Failed to fetch page: {url}")
                return None

            # データを抽出
            data = await self._extraction_manager.extract_data(
                url=url,
                content=content,
                target_fields=target_fields
            )
            if not data:
                logger.warning(f"No data extracted from: {url}")
                return None

            # 必須フィールドの検証
            missing_fields = self._field_validator.get_missing_fields(
                data,
                target_fields
            )
            if missing_fields:
                logger.warning(
                    f"Missing required fields {missing_fields} in data from: {url}"
                )
                return None

            return data

        except Exception as e:
            logger.error(f"Data collection failed for {url}: {e}")
            return None 
