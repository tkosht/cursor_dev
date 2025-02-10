"""
Twitter APIクライアント

ブックマークの取得と管理を行うモジュール（MVP版）
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


class TwitterClientError(Exception):
    """TwitterClient固有のエラー"""
    pass


class TwitterClient:
    """Twitter APIクライアントクラス（MVP版）"""

    # Twitterステータスの正規表現パターン
    TWITTER_STATUS_PATTERN = r'^https://twitter\.com/\w+/status/\d+$'

    def __init__(self, bookmarks_file: Optional[str] = None):
        """
        TwitterClientの初期化

        Args:
            bookmarks_file: ブックマークデータを保存するJSONファイルのパス
                          （デフォルト: ~/workspace/data/bookmarks.json）

        Raises:
            TwitterClientError: ブックマークファイルの初期化に失敗した場合
        """
        if bookmarks_file is None:
            self.bookmarks_file = os.path.expanduser('~/workspace/data/bookmarks.json')
        else:
            self.bookmarks_file = bookmarks_file

        try:
            # データディレクトリの作成を試みる
            directory = os.path.dirname(self.bookmarks_file)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except OSError as e:
                    raise TwitterClientError(f"ディレクトリの作成に失敗: {e}")

            # 初期データの作成
            if not os.path.exists(self.bookmarks_file):
                self._save_bookmarks([])
        except Exception as e:
            raise TwitterClientError(f"ブックマークファイルの初期化に失敗: {e}")

    def _load_bookmarks(self) -> List[Dict]:
        """保存されているブックマークを読み込む"""
        try:
            with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise TwitterClientError(f"ブックマークファイルの解析に失敗: {e}")
        except IOError as e:
            raise TwitterClientError(f"ブックマークファイルの読み込みに失敗: {e}")

    def _save_bookmarks(self, bookmarks: List[Dict]) -> None:
        """ブックマークを保存する"""
        try:
            # ディレクトリが存在することを確認
            directory = os.path.dirname(self.bookmarks_file)
            if not os.path.exists(directory):
                raise TwitterClientError(f"保存先ディレクトリが存在しません: {directory}")

            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise TwitterClientError(f"ブックマークファイルの保存に失敗: {e}")
        except Exception as e:
            raise TwitterClientError(f"ブックマークの保存に失敗: {e}")

    def _validate_url(self, url: str) -> None:
        """URLの形式を検証する"""
        if not url:
            raise TwitterClientError("無効なURL: URLが空です")
        if not re.match(self.TWITTER_STATUS_PATTERN, url):
            raise TwitterClientError("無効なURL: TwitterのステータスURLではありません")

    def _validate_text(self, text: str) -> None:
        """テキストの内容を検証する"""
        if not text or text.isspace():
            raise TwitterClientError("テキストが空です")

    async def import_bookmarks_html(self, html_file: str) -> List[Dict]:
        """
        ブラウザからエクスポートしたブックマークのHTMLファイルを読み込む

        Args:
            html_file: ブックマークのHTMLファイルパス

        Returns:
            List[Dict]: インポートされたブックマークのリスト

        Raises:
            TwitterClientError: HTMLファイルの読み込みや解析に失敗した場合
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            soup = BeautifulSoup(content, 'html.parser')
            if not soup.find_all('a'):  # リンクが1つも見つからない場合
                raise TwitterClientError("有効なブックマークが見つかりません")

            bookmarks = []
            for link in soup.find_all('a'):
                url = link.get('href', '')
                self._validate_url(url)  # URLの検証
                text = link.get_text()
                self._validate_text(text)  # テキストの検証
                
                bookmark = {
                    'id': url.split('/')[-1],
                    'url': url,
                    'text': text,
                    'created_at': link.get('add_date', ''),
                }
                bookmarks.append(bookmark)

            self._save_bookmarks(bookmarks)
            return bookmarks
        except (IOError, Exception) as e:
            raise TwitterClientError(f"HTMLファイルのインポートに失敗: {e}")

    async def get_bookmarks(self, max_results: int = 100) -> List[Dict]:
        """
        保存されているブックマークを取得する

        Args:
            max_results: 取得する最大件数（デフォルト: 100）

        Returns:
            List[Dict]: ブックマークのリスト

        Raises:
            TwitterClientError: ブックマークの取得に失敗した場合
        """
        try:
            bookmarks = self._load_bookmarks()
            return bookmarks[:max_results]
        except Exception as e:
            raise TwitterClientError(f"ブックマークの取得に失敗: {e}")

    async def get_bookmark_updates(self, since: datetime) -> List[Dict]:
        """
        指定時刻以降のブックマーク更新を取得する

        Args:
            since: この時刻以降の更新を取得

        Returns:
            List[Dict]: 更新されたブックマークのリスト

        Raises:
            TwitterClientError: ブックマーク更新の取得に失敗した場合
        """
        try:
            bookmarks = self._load_bookmarks()
            since_timestamp = since.timestamp()
            return [
                b for b in bookmarks
                if float(b.get('created_at', 0)) >= since_timestamp
            ]
        except Exception as e:
            raise TwitterClientError(f"ブックマーク更新の取得に失敗: {e}")

    async def add_bookmark(self, url: str, text: str) -> Dict:
        """
        新しいブックマークを追加する

        Args:
            url: ブックマークのURL
            text: ブックマークのテキスト

        Returns:
            Dict: 追加されたブックマーク

        Raises:
            TwitterClientError: ブックマークの追加に失敗した場合
        """
        try:
            self._validate_url(url)  # URLの検証
            self._validate_text(text)  # テキストの検証

            bookmark = {
                'id': url.split('/')[-1],
                'url': url,
                'text': text,
                'created_at': str(datetime.now().timestamp()),
            }

            bookmarks = self._load_bookmarks()
            bookmarks.append(bookmark)
            self._save_bookmarks(bookmarks)

            return bookmark
        except Exception as e:
            raise TwitterClientError(f"ブックマークの追加に失敗: {e}") 