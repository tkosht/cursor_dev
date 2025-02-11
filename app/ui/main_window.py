"""
メインウィンドウ

アプリケーションのメインウィンドウを提供するモジュール
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Dict, List

from ..logger import CustomLogger


class MainWindowError(Exception):
    """MainWindow固有のエラー"""

    pass


class MainWindow:
    """メインウィンドウクラス"""

    def __init__(
        self, title: str = "ブックマーク検索", geometry: str = "800x600"
    ):
        """
        MainWindowの初期化

        Args:
            title: ウィンドウのタイトル（デフォルト: "ブックマーク検索"）
            geometry: ウィンドウのサイズ（デフォルト: "800x600"）
        """
        self.logger = CustomLogger(__name__)
        self.logger.info(
            "メインウィンドウの初期化を開始",
            {"title": title, "geometry": geometry},
        )

        try:
            self.root = tk.Tk()
            self.root.title(title)
            self.root.geometry(geometry)

            self._setup_ui()
            self.logger.info("メインウィンドウの初期化が完了")

        except Exception as e:
            error_msg = f"メインウィンドウの初期化に失敗: {e}"
            self.logger.error(error_msg)
            raise MainWindowError(error_msg)

    def _setup_ui(self) -> None:
        """UIコンポーネントのセットアップ"""
        self.logger.debug("UIコンポーネントのセットアップを開始")
        try:
            # 検索フレーム
            search_frame = ttk.Frame(self.root, padding="10")
            search_frame.pack(fill=tk.X)

            # 検索入力
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(
                search_frame, textvariable=self.search_var, width=50
            )
            search_entry.pack(side=tk.LEFT, padx=(0, 10))

            # 検索ボタン
            search_button = ttk.Button(
                search_frame, text="検索", command=self._on_search
            )
            search_button.pack(side=tk.LEFT)

            # 結果表示エリア
            result_frame = ttk.Frame(self.root, padding="10")
            result_frame.pack(fill=tk.BOTH, expand=True)

            # 結果リスト
            self.result_tree = ttk.Treeview(
                result_frame,
                columns=("title", "url", "score"),
                show="headings",
            )
            self.result_tree.heading("title", text="タイトル")
            self.result_tree.heading("url", text="URL")
            self.result_tree.heading("score", text="スコア")
            self.result_tree.pack(fill=tk.BOTH, expand=True)

            self.logger.debug("UIコンポーネントのセットアップが完了")

        except Exception as e:
            error_msg = f"UIコンポーネントのセットアップに失敗: {e}"
            self.logger.error(error_msg)
            raise MainWindowError(error_msg)

    def _on_search(self) -> None:
        """検索ボタンクリック時の処理"""
        query = self.search_var.get().strip()
        self.logger.info("検索が開始されました", {"query": query})

        if not query:
            self.logger.warning("検索クエリが空です")
            messagebox.showwarning("警告", "検索キーワードを入力してください")
            return

        try:
            # TODO: 検索エンジンとの連携
            # results = search_engine.search(query)
            # self.display_results(results)
            self.logger.debug("検索エンジンとの連携は未実装")
            messagebox.showinfo("情報", "検索機能は現在実装中です")

        except Exception as e:
            error_msg = f"検索処理中にエラーが発生: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("エラー", "検索中にエラーが発生しました")

    def display_results(self, results: List[Dict]) -> None:
        """
        検索結果を表示する

        Args:
            results: 検索結果のリスト
        """
        self.logger.info(
            "検索結果の表示を開始", {"results_count": len(results)}
        )
        try:
            # 既存の結果をクリア
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # 新しい結果を表示
            for result in results:
                self.result_tree.insert(
                    "",
                    tk.END,
                    values=(
                        result.get("title", "不明"),
                        result.get("url", "不明"),
                        f"{result.get('score', 0):.3f}",
                    ),
                )

            self.logger.debug("検索結果の表示が完了")

        except Exception as e:
            error_msg = f"検索結果の表示に失敗: {e}"
            self.logger.error(error_msg)
            raise MainWindowError(error_msg)

    def set_search_callback(
        self, callback: Callable[[str], List[Dict]]
    ) -> None:
        """
        検索コールバックを設定する

        Args:
            callback: 検索処理を行うコールバック関数
        """
        self.logger.debug("検索コールバックを設定")
        self._search_callback = callback

    def run(self) -> None:
        """メインウィンドウを実行する"""
        self.logger.info("メインウィンドウを開始")
        try:
            self.root.mainloop()
        except Exception as e:
            error_msg = f"メインウィンドウの実行中にエラーが発生: {e}"
            self.logger.error(error_msg)
            raise MainWindowError(error_msg)
