"""HTMLコンテンツを解析するモジュール。"""

import logging
import re
from datetime import datetime
from typing import Dict, Optional

from bs4 import BeautifulSoup

from app.exceptions import ContentParseError

logger = logging.getLogger(__name__)


class ContentParser:
    """HTMLコンテンツを解析するクラス。"""

    def __init__(self):
        """初期化。"""
        self._unwanted_tags = ['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'nav']

    def parse_content(self, html: str) -> Dict[str, str]:
        """HTMLコンテンツを解析する。

        Args:
            html: HTMLコンテンツ

        Returns:
            Dict[str, str]: 解析結果
                - title: タイトル
                - content: 本文
                - date: 日付（ISO形式）
                - url: URL

        Raises:
            ContentParseError: 解析に失敗した場合
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            self._remove_unwanted_tags(soup)

            title = self._extract_title(soup)
            content = self._extract_content(soup)
            date = self._extract_date(soup)

            if not title or not content:
                logger.error("必須コンテンツが見つかりません")
                raise ContentParseError("必須コンテンツが見つかりません")

            return {
                'title': title,
                'content': content,
                'date': date.isoformat() if date else None,
                'url': self._extract_canonical_url(soup)
            }

        except Exception as e:
            logger.error(f"コンテンツの解析に失敗しました: {str(e)}")
            raise ContentParseError(f"コンテンツの解析に失敗しました: {str(e)}")

    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> None:
        """不要なタグを削除する。

        Args:
            soup: BeautifulSoupオブジェクト
        """
        for tag in self._unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """タイトルを抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: タイトル
        """
        # h1タグを優先的に使用
        h1_tag = soup.find('h1')
        if h1_tag:
            return self._normalize_text(h1_tag.string)

        # og:titleメタタグを次に使用
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return self._normalize_text(og_title.get('content'))

        # 最後にtitleタグを使用
        title_tag = soup.find('title')
        if title_tag:
            return self._normalize_text(title_tag.string)

        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """本文を抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: 本文
        """
        article = soup.find('article')
        if article:
            return self._normalize_text(article.get_text())

        main = soup.find('main')
        if main:
            return self._normalize_text(main.get_text())

        # 最も長いテキストブロックを探す
        text_blocks = []
        for tag in soup.find_all(['p', 'div']):
            text = self._normalize_text(tag.get_text())
            if text:
                text_blocks.append(text)

        if text_blocks:
            return max(text_blocks, key=len)

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """日付を抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[datetime]: 日付
        """
        # メタデータから日付を抽出
        date = self._extract_date_from_meta(soup)
        if date:
            return date

        # テキストから日付を抽出
        return self._extract_date_from_text(soup)

    def _extract_date_from_meta(self, soup: BeautifulSoup) -> Optional[datetime]:
        """メタデータから日付を抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[datetime]: 日付
        """
        date_tag = (
            soup.find('meta', property='article:published_time') or
            soup.find('time') or
            soup.find('meta', property='og:article:published_time')
        )

        if date_tag:
            date_str = date_tag.get('content') or date_tag.get('datetime')
            if date_str:
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    pass
        return None

    def _extract_date_from_text(self, soup: BeautifulSoup) -> Optional[datetime]:
        """テキストから日付を抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[datetime]: 日付
        """
        date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'
        for tag in soup.find_all(['p', 'span', 'div']):
            match = re.search(date_pattern, tag.get_text())
            if match:
                date = self._parse_date_string(match.group())
                if date:
                    return date
        return None

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """日付文字列をパースする。

        Args:
            date_str: 日付文字列

        Returns:
            Optional[datetime]: 日付
        """
        formats = ['%Y-%m-%d', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _extract_canonical_url(self, soup: BeautifulSoup) -> Optional[str]:
        """正規URLを抽出する。

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: 正規URL
        """
        canonical = soup.find('link', rel='canonical')
        if canonical:
            return canonical.get('href')
        return None

    def _normalize_text(self, text: Optional[str]) -> Optional[str]:
        """テキストを正規化する。

        Args:
            text: テキスト

        Returns:
            Optional[str]: 正規化されたテキスト
        """
        if not text:
            return None

        # 改行と空白を正規化
        text = re.sub(r'\s+', ' ', text.strip())
        # 全角スペースを半角に
        text = text.replace('　', ' ')
        return text 