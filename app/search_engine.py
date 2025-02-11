"""
検索エンジン

ブックマークの検索機能を提供するモジュール
"""

import os
from typing import Dict, List, Tuple

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from .logger import CustomLogger


class SearchEngineError(Exception):
    """SearchEngine固有のエラー"""

    pass


class SearchEngine:
    """検索エンジンクラス"""

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-large",
        index_dir: str = None,
        use_gpu: bool = True,
    ):
        """
        SearchEngineの初期化

        Args:
            model_name: 使用する文章埋め込みモデル名（デフォルト: intfloat/multilingual-e5-large）
            index_dir: インデックスファイルを保存するディレクトリ
                      （デフォルト: ~/workspace/data/search_index）
            use_gpu: GPUを使用するかどうか（デフォルト: True）
        """
        self.logger = CustomLogger(__name__)
        self.logger.info(
            "SearchEngineの初期化を開始",
            {
                "model_name": model_name,
                "index_dir": index_dir,
                "use_gpu": use_gpu,
            },
        )

        try:
            self.model = SentenceTransformer(model_name)
            if torch.cuda.is_available() and use_gpu:
                self.model = self.model.to("cuda")
                self.logger.info("モデルをGPUに移動")
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.use_gpu = use_gpu and torch.cuda.is_available()

            if index_dir is None:
                self.index_dir = os.path.expanduser(
                    "~/workspace/data/search_index"
                )
            else:
                self.index_dir = index_dir

            os.makedirs(self.index_dir, exist_ok=True)
            self.index_file = os.path.join(self.index_dir, "faiss.index")
            self.bookmarks_file = os.path.join(self.index_dir, "bookmarks.npy")

            # インデックスの読み込みまたは新規作成
            if os.path.exists(self.index_file):
                self.logger.info(
                    "既存のインデックスを読み込み", {"file": self.index_file}
                )
                self.index = faiss.read_index(self.index_file)
            else:
                self.logger.info(
                    "新規インデックスを作成", {"dimension": self.dimension}
                )
                self.index = faiss.IndexFlatL2(self.dimension)

            # GPUが利用可能な場合、インデックスをGPUに移動
            if self.use_gpu:
                self.logger.info("インデックスをGPUに移動")
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)

            if os.path.exists(self.bookmarks_file):
                self.logger.info(
                    "既存のブックマークデータを読み込み",
                    {"file": self.bookmarks_file},
                )
                self.bookmarks = np.load(
                    self.bookmarks_file, allow_pickle=True
                ).tolist()
            else:
                self.logger.info("新規ブックマークリストを作成")
                self.bookmarks: List[Dict] = []
                self._save_index()

            self.logger.info(
                "SearchEngineの初期化が完了",
                {
                    "total_bookmarks": len(self.bookmarks),
                    "dimension": self.dimension,
                    "use_gpu": self.use_gpu,
                },
            )

        except Exception as e:
            error_msg = f"SearchEngineの初期化に失敗: {e}"
            self.logger.error(error_msg)
            raise SearchEngineError(error_msg)

    def _save_index(self) -> None:
        """インデックスを保存する"""
        self.logger.debug("インデックスの保存を開始")
        try:
            # GPUインデックスの場合、保存前にCPUに移動
            if self.use_gpu:
                self.logger.debug("GPUインデックスをCPUに移動")
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                faiss.write_index(cpu_index, self.index_file)
            else:
                faiss.write_index(self.index, self.index_file)
            np.save(
                self.bookmarks_file, np.array(self.bookmarks, dtype=object)
            )
            self.logger.info(
                "インデックスの保存が完了",
                {
                    "index_file": self.index_file,
                    "bookmarks_file": self.bookmarks_file,
                    "total_bookmarks": len(self.bookmarks),
                },
            )
        except Exception as e:
            error_msg = f"インデックスの保存に失敗: {e}"
            self.logger.error(error_msg)
            raise SearchEngineError(error_msg)

    def add_bookmarks(self, bookmarks: List[Dict]) -> None:
        """
        ブックマークを検索インデックスに追加する

        Args:
            bookmarks: 追加するブックマークのリスト
        """
        if not bookmarks:
            self.logger.info("追加するブックマークが空のため処理をスキップ")
            return

        self.logger.info("ブックマークの追加を開始", {"count": len(bookmarks)})
        try:
            # E5モデル用のプレフィックス "query: " を追加
            texts = [f"passage: {bookmark['text']}" for bookmark in bookmarks]
            self.logger.debug(
                "埋め込みベクトルの生成を開始", {"texts_count": len(texts)}
            )
            embeddings = self.model.encode(texts)
            self.logger.debug("インデックスへの追加を開始")
            self.index.add(np.array(embeddings).astype("float32"))
            self.bookmarks.extend(bookmarks)
            self._save_index()
            self.logger.info(
                "ブックマークの追加が完了",
                {
                    "added_count": len(bookmarks),
                    "total_bookmarks": len(self.bookmarks),
                },
            )
        except Exception as e:
            error_msg = f"ブックマークの追加に失敗: {e}"
            self.logger.error(error_msg)
            raise SearchEngineError(error_msg)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        クエリに関連するブックマークを検索する

        Args:
            query: 検索クエリ
            top_k: 返す結果の最大数（デフォルト: 5）

        Returns:
            List[Tuple[Dict, float]]: (ブックマーク, スコア) のタプルのリスト
                                    スコアが小さいほど類似度が高い
        """
        if not self.bookmarks:
            self.logger.info("ブックマークが存在しないため空の結果を返す")
            return []

        self.logger.info("検索を開始", {"query": query, "top_k": top_k})
        try:
            # E5モデル用のプレフィックス "query: " を追加
            query_embedding = self.model.encode([f"query: {query}"])
            self.logger.debug("クエリの埋め込みベクトルを生成")

            distances, indices = self.index.search(
                np.array(query_embedding).astype("float32"),
                min(top_k, len(self.bookmarks)),
            )
            self.logger.debug("検索が完了", {"results_count": len(indices[0])})

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                results.append((self.bookmarks[idx], float(dist)))

            self.logger.info(
                "検索結果を返却",
                {
                    "results_count": len(results),
                    "min_distance": (
                        float(min(distances[0]))
                        if len(distances[0]) > 0
                        else None
                    ),
                    "max_distance": (
                        float(max(distances[0]))
                        if len(distances[0]) > 0
                        else None
                    ),
                },
            )
            return results
        except Exception as e:
            error_msg = f"検索に失敗: {e}"
            self.logger.error(error_msg)
            raise SearchEngineError(error_msg)

    def clear(self) -> None:
        """インデックスをクリアする"""
        self.logger.info("インデックスのクリアを開始")
        try:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.bookmarks = []
            self._save_index()
            self.logger.info("インデックスのクリアが完了")
        except Exception as e:
            error_msg = f"インデックスのクリアに失敗: {e}"
            self.logger.error(error_msg)
            raise SearchEngineError(error_msg)

    def get_total_bookmarks(self) -> int:
        """
        インデックスされているブックマークの総数を返す

        Returns:
            int: ブックマークの総数
        """
        count = len(self.bookmarks)
        self.logger.debug("ブックマーク総数を取得", {"count": count})
        return count
