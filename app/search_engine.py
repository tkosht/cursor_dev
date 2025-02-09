"""
検索エンジン

ブックマークの検索機能を提供するモジュール
"""

from typing import Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class SearchEngine:
    """検索エンジンクラス"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        SearchEngineの初期化

        Args:
            model_name: 使用する文章埋め込みモデル名（デフォルト: all-MiniLM-L6-v2）
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.bookmarks: List[Dict] = []

    def add_bookmarks(self, bookmarks: List[Dict]) -> None:
        """
        ブックマークを検索インデックスに追加する

        Args:
            bookmarks: 追加するブックマークのリスト
        """
        if not bookmarks:
            return

        texts = [bookmark["text"] for bookmark in bookmarks]
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.bookmarks.extend(bookmarks)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        クエリに関連するブックマークを検索する

        Args:
            query: 検索クエリ
            top_k: 返す結果の最大数（デフォルト: 5）

        Returns:
            List[Dict]: 関連度順のブックマークリスト
        """
        if not self.bookmarks:
            return []

        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            min(top_k, len(self.bookmarks))
        )

        results = []
        for idx in indices[0]:
            results.append(self.bookmarks[idx])

        return results 
