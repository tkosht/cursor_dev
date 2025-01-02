"""Extraction manager for handling data extraction from web pages."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from ..exceptions import ExtractionError, NoValidDataError
from ..monitoring.monitor import Monitor

logger = logging.getLogger(__name__)


class ExtractionManager:
    """Manager class for extracting data from web pages."""

    def __init__(self, monitor: Optional[Monitor] = None):
        """Initialize the extraction manager.

        Args:
            monitor: Optional monitor for tracking extraction metrics.
        """
        self.monitor = monitor or Monitor()

    async def extract_data(
        self,
        content: str,
        url: str,
        target_fields: List[str]
    ) -> Dict[str, Any]:
        """Extract data from HTML content using target fields.

        Args:
            content: HTML content to extract data from.
            url: The URL where the content was obtained from.
            target_fields: List of fields to extract.

        Returns:
            Dictionary containing the extracted data.

        Raises:
            ExtractionError: If data extraction fails.
            NoValidDataError: If no valid data could be extracted.
        """
        try:
            data = await self._extract_fields(content, url, target_fields)
            if not data:
                raise NoValidDataError(f"No valid data could be extracted from {url}")
            return data

        except Exception as e:
            logger.error(f"Data extraction failed for {url}: {e}")
            raise ExtractionError(f"Data extraction failed: {e}")

    async def _extract_fields(
        self,
        content: str,
        url: str,
        target_fields: List[str]
    ) -> Dict[str, Any]:
        """Extract specified fields from HTML content.

        Args:
            content: HTML content to extract data from.
            url: The URL where the content was obtained from.
            target_fields: List of fields to extract.

        Returns:
            Dictionary containing the extracted data.
        """
        soup = BeautifulSoup(content, "html.parser")
        data = {}

        for field in target_fields:
            value = await self._extract_single_field(soup, field, url)
            if value:
                if field == "date":
                    normalized_date = self._normalize_date(value)
                    if normalized_date:
                        data[field] = normalized_date
                else:
                    data[field] = value

        return data

    async def _extract_single_field(
        self,
        soup: BeautifulSoup,
        field: str,
        url: str
    ) -> Optional[str]:
        """Extract a single field from parsed HTML.

        Args:
            soup: BeautifulSoup object.
            field: Field name to extract.
            url: URL for logging purposes.

        Returns:
            Extracted value or None if not found.
        """
        try:
            selectors = self._generate_selectors(field)
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    value = elements[0].get_text(strip=True)
                    if value and self._validate_field_value(field, value):
                        return value

            # メタタグからの抽出を試みる
            meta_value = self._extract_from_meta(soup, field)
            if meta_value and self._validate_field_value(field, meta_value):
                return meta_value

            logger.warning(f"No data found for field '{field}' at {url}")
            return None

        except Exception as e:
            logger.error(f"Failed to extract {field} at {url}: {e}")
            return None

    def _generate_selectors(self, field: str) -> List[str]:
        """Generate CSS selectors for a given field.

        Args:
            field: Field name to generate selectors for.

        Returns:
            List of CSS selectors.
        """
        # フィールドに応じたセレクタを定義
        selectors = {
            "title": [
                "h1",
                "title",
                ".title",
                "#title",
                "meta[property='og:title']",
                "meta[name='title']",
                ".article-title",
                ".news-title",
                ".headline",
                "header h1",
                "article h1",
                "main h1",
                ".page-title",
                ".entry-title",
                ".post-title"
            ],
            "date": [
                "time",
                ".date",
                "#date",
                "meta[property='article:published_time']",
                "meta[name='date']",
                ".published-date",
                ".timestamp",
                ".article-date",
                ".news-date",
                ".release-date",
                "header time",
                "article time",
                "[datetime]",
                "[itemprop='datePublished']",
                "[itemprop='dateModified']",
                ".entry-date",
                ".post-date",
                ".publish-date",
                ".update-date",
                ".modified-date"
            ],
            "content": [
                "article",
                ".article-content",
                "#article-content",
                ".content",
                "#content",
                "main",
                ".article-body",
                ".news-content",
                ".release-content",
                "[itemprop='articleBody']",
                "[itemprop='description']",
                ".description",
                "#description",
                "meta[property='og:description']",
                "meta[name='description']",
                ".entry-content",
                ".post-content",
                ".main-content",
                ".body-content",
                ".article-text"
            ],
            "summary": [
                ".summary",
                "#summary",
                ".abstract",
                "#abstract",
                ".description",
                "#description",
                "meta[property='og:description']",
                "meta[name='description']",
                ".article-summary",
                ".news-summary",
                ".excerpt",
                ".entry-summary",
                ".post-summary",
                ".lead-text",
                ".introduction"
            ],
            "author": [
                ".author",
                "#author",
                "[itemprop='author']",
                "meta[name='author']",
                ".article-author",
                ".news-author",
                ".byline",
                ".writer",
                ".contributor",
                ".entry-author"
            ],
            "category": [
                ".category",
                "#category",
                "[itemprop='articleSection']",
                "meta[property='article:section']",
                ".article-category",
                ".news-category",
                ".topic",
                ".section",
                ".entry-category",
                ".post-category"
            ],
            "tags": [
                ".tags",
                "#tags",
                "[itemprop='keywords']",
                "meta[name='keywords']",
                ".article-tags",
                ".news-tags",
                ".entry-tags",
                ".post-tags",
                ".topic-tags",
                ".content-tags"
            ]
        }

        # フィールドに対応するセレクタがない場合はデフォルトを返す
        return selectors.get(field, [f".{field}", f"#{field}"])

    def _validate_field_value(self, field: str, value: str) -> bool:
        """Validate the extracted field value.

        Args:
            field: Field name to validate.
            value: Value to validate.

        Returns:
            bool: Whether the value is valid.
        """
        if not value:
            return False

        if field == "date":
            # 日付形式の検証
            date_patterns = [
                r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY-MM-DD or YYYY/MM/DD
                r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",  # DD-MM-YYYY or DD/MM/YYYY
                r"\d{4}年\d{1,2}月\d{1,2}日",    # YYYY年MM月DD日
                r"\d{4}\.\d{1,2}\.\d{1,2}",      # YYYY.MM.DD
                r"\d{1,2}\.\d{1,2}\.\d{4}"       # DD.MM.YYYY
            ]
            return any(re.search(pattern, value) for pattern in date_patterns)

        if field == "content":
            # コンテンツの最小長を検証
            return len(value) >= 50  # 最低50文字

        if field == "title":
            # タイトルの最小長と最大長を検証
            return 3 <= len(value) <= 200

        # その他のフィールドは単純な長さチェック
        return len(value) > 0

    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to YYYY-MM-DD format.

        Args:
            date_str: Date string to normalize.

        Returns:
            Optional[str]: Normalized date string or None if invalid.
        """
        try:
            # 日付パターンとそのパース方法を定義
            patterns = [
                (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", "%Y-%m-%d"),
                (r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", "%d-%m-%Y"),
                (r"(\d{4})年(\d{1,2})月(\d{1,2})日", "%Y年%m月%d日"),
                (r"(\d{4})\.(\d{1,2})\.(\d{1,2})", "%Y.%m.%d"),
                (r"(\d{1,2})\.(\d{1,2})\.(\d{4})", "%d.%m.%Y")
            ]

            for pattern, format_str in patterns:
                match = re.search(pattern, date_str)
                if match:
                    date = datetime.strptime(match.group(), format_str)
                    return date.strftime("%Y-%m-%d")

            return None

        except Exception as e:
            logger.error(f"Failed to normalize date {date_str}: {e}")
            return None

    def _extract_from_meta(self, soup: BeautifulSoup, field: str) -> Optional[str]:
        """Extract value from meta tags.

        Args:
            soup: BeautifulSoup object.
            field: Field name to extract.

        Returns:
            Optional[str]: Extracted value or None if not found.
        """
        try:
            # メタタグのマッピング
            meta_mapping = {
                "title": [
                    "og:title",
                    "twitter:title",
                    "title",
                    "dc.title"
                ],
                "date": [
                    "article:published_time",
                    "article:modified_time",
                    "date",
                    "dc.date",
                    "pubdate"
                ],
                "content": [
                    "og:description",
                    "twitter:description",
                    "description",
                    "dc.description"
                ],
                "author": [
                    "author",
                    "dc.creator",
                    "article:author"
                ],
                "category": [
                    "article:section",
                    "category",
                    "dc.subject"
                ],
                "tags": [
                    "keywords",
                    "news_keywords",
                    "article:tag"
                ]
            }

            # メタタグから値を抽出
            meta_names = meta_mapping.get(field, [field])
            for name in meta_names:
                # property属性を持つメタタグを検索
                meta = soup.find("meta", property=name)
                if meta and meta.get("content"):
                    return meta.get("content")

                # name属性を持つメタタグを検索
                meta = soup.find("meta", attrs={"name": name})
                if meta and meta.get("content"):
                    return meta.get("content")

            return None

        except Exception as e:
            logger.error(f"Failed to extract from meta tags: {e}")
            return None

    async def extract_multiple(
        self,
        contents: List[str],
        urls: List[str],
        target_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Extract data from multiple HTML contents concurrently.

        Args:
            contents: List of HTML contents to extract data from.
            urls: List of URLs where the contents were obtained from.
            target_fields: List of fields to extract.

        Returns:
            List of dictionaries containing the extracted data.
        """
        if len(contents) != len(urls):
            raise ValueError("Number of contents must match number of URLs")

        tasks = [
            self.extract_data(content, url, target_fields)
            for content, url in zip(contents, urls)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        extracted_data = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to extract data from {url}: {result}")
                continue
            extracted_data.append(result)

        return extracted_data 