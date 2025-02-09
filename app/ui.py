"""
Gradio UI

ユーザーインターフェースを提供するモジュール
"""

from typing import Dict, List, Tuple

import gradio as gr

from .llm_processor import LLMProcessor
from .search_engine import SearchEngine
from .twitter_client import TwitterClient


class UI:
    """UI管理クラス"""

    def __init__(
        self,
        twitter_client: TwitterClient,
        search_engine: SearchEngine,
        llm_processor: LLMProcessor
    ):
        """
        UIの初期化

        Args:
            twitter_client: Twitter APIクライアント
            search_engine: 検索エンジン
            llm_processor: LLM処理
        """
        self.twitter_client = twitter_client
        self.search_engine = search_engine
        self.llm_processor = llm_processor

    async def search_and_respond(
        self,
        query: str,
        top_k: int = 5,
        model_type: str = "gemini"
    ) -> Tuple[str, List[Dict]]:
        """
        検索と回答生成を実行

        Args:
            query: 検索クエリ
            top_k: 取得する結果の数
            model_type: 使用するLLMの種類

        Returns:
            Tuple[str, List[Dict]]: 生成された回答とブックマークのリスト
        """
        # 検索実行
        results = self.search_engine.search(query, top_k=top_k)
        
        # LLMで回答生成
        response = await self.llm_processor.generate_response(query, results)
        
        return response, results

    def create_interface(self) -> gr.Blocks:
        """
        Gradioインターフェースを作成

        Returns:
            gr.Blocks: Gradioインターフェース
        """
        with gr.Blocks(title="X Bookmark RAG") as interface:
            gr.Markdown("# X Bookmark RAG")
            gr.Markdown("Xのブックマークを検索し、AIが回答を生成します。")

            with gr.Row():
                with gr.Column():
                    query = gr.Textbox(
                        label="検索クエリ",
                        placeholder="検索したい内容を入力してください..."
                    )
                    top_k = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="取得する結果の数"
                    )
                    model_type = gr.Dropdown(
                        choices=["gemini", "gpt", "claude", "ollama"],
                        value="gemini",
                        label="使用するLLM"
                    )
                    search_button = gr.Button("検索")

                with gr.Column():
                    response = gr.Markdown(label="AI回答")
                    results = gr.JSON(label="検索結果")

            search_button.click(
                fn=self.search_and_respond,
                inputs=[query, top_k, model_type],
                outputs=[response, results]
            )

        return interface

    def launch(self, **kwargs):
        """
        UIを起動

        Args:
            **kwargs: Gradio launchメソッドに渡す引数
        """
        interface = self.create_interface()
        interface.launch(**kwargs) 
