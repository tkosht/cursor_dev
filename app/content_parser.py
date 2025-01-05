"""HTMLコンテンツから必要な情報を抽出するモジュール。"""

import logging
from typing import Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentParser:
    """HTMLコンテンツから本文や見出しなどを抽出するクラス。"""

    def __init__(self):
        """ContentParserを初期化する。"""
        self.unwanted_tags = {
            'script', 'style', 'iframe', 'form',
            'nav', 'header', 'footer', 'aside'
        }

    def parse_html(self, raw_html: str) -> Dict[str, str]:
        """
        HTMLから本文やタイトル、日付などを抽出する。

        Args:
            raw_html (str): 解析対象のHTML文字列

        Returns:
            Dict[str, str]: {
                "title": "ページタイトル",
                "content": "本文",
                "date": "日付" (存在する場合)
            }

        Raises:
            ValueError: HTMLの解析に失敗した場合
        """
        if not raw_html:
            raise ValueError("HTMLが空です。")

        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            soup = self._remove_unwanted_tags(soup)

            result = {
                "title": self._extract_title(soup),
                "content": self._extract_content(soup)
            }

            date = self._extract_date(soup)
            if date:
                result["date"] = date

            return result

        except Exception as e:
            logger.error(f"HTML解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"HTMLの解析に失敗しました: {str(e)}")

    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        不要なタグを削除する。

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            BeautifulSoup: 不要タグを削除したBeautifulSoupオブジェクト
        """
        for tag in self.unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        return soup

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        タイトルを抽出する。

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            str: 抽出したタイトル
        """
        title_tag = soup.title
        if title_tag and title_tag.string:
            return self._normalize_text(title_tag.string)

        h1_tag = soup.find('h1')
        if h1_tag:
            return self._normalize_text(h1_tag.get_text())

        return "タイトルなし"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        本文を抽出する。

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            str: 抽出した本文
        """
        # article, main, divタグの順で探索
        for tag in ['article', 'main']:
            content = soup.find(tag)
            if content:
                return self._normalize_text(content.get_text())

        # 上記タグがない場合は、最も長いテキストを含むdivを探す
        divs = soup.find_all('div')
        if divs:
            main_div = max(divs, key=lambda x: len(x.get_text()))
            return self._normalize_text(main_div.get_text())

        # どれも見つからない場合は、bodyの全テキストを返す
        return self._normalize_text(soup.body.get_text() if soup.body else "")

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        日付情報を抽出する。

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            Optional[str]: 抽出した日付（見つからない場合はNone）
        """
        # time要素を探す
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']

        # meta要素の日付を探す
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['article:published_time', 'og:published_time']:
                return meta.get('content')

        return None

    def _normalize_text(self, text: str) -> str:
        """
        テキストを正規化する。

        Args:
            text (str): 正規化対象のテキスト

        Returns:
            str: 正規化したテキスト
        """
        if not text:
            return ""

        # 改行や空白を調整
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines) 