"""
Twitter APIクライアント

ブックマークの取得と管理を行うモジュール（MVP版）
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


class TwitterClientError(Exception):
    """TwitterClient固有のエラー"""
    pass


class TwitterClient:
    """Twitter APIクライアントクラス（MVP版）"""

    def __init__(self, bookmarks_file: Optional[str] = None):
        """
        TwitterClientの初期化

        Args:
            bookmarks_file: ブックマークデータを保存するJSONファイルのパス
                          （デフォルト: ~/workspace/data/bookmarks.json）
        """
        if bookmarks_file is None:
            self.bookmarks_file = os.path.expanduser('~/workspace/data/bookmarks.json')
        else:
            self.bookmarks_file = bookmarks_file

        # データディレクトリの作成
        os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)

        # 初期データの作成
        if not os.path.exists(self.bookmarks_file):
            self._save_bookmarks([])

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
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise TwitterClientError(f"ブックマークファイルの保存に失敗: {e}")

    async def import_bookmarks_html(self, html_file: str) -> List[Dict]:
        """
        ブラウザからエクスポートしたブックマークのHTMLファイルを読み込む

        Args:
            html_file: ブックマークのHTMLファイルパス

        Returns:
            List[Dict]: インポートされたブックマークのリスト
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            bookmarks = []
            for link in soup.find_all('a'):
                bookmark = {
                    'id': link.get('href', '').split('/')[-1],
                    'url': link.get('href', ''),
                    'text': link.get_text(),
                    'created_at': link.get('add_date', ''),
                }
                bookmarks.append(bookmark)

            self._save_bookmarks(bookmarks)
            return bookmarks
        except Exception as e:
            raise TwitterClientError(f"HTMLファイルのインポートに失敗: {e}")

    async def get_bookmarks(self, max_results: int = 100) -> List[Dict]:
        """
        保存されているブックマークを取得する

        Args:
            max_results: 取得する最大件数（デフォルト: 100）

        Returns:
            List[Dict]: ブックマークのリスト
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
        """
        try:
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