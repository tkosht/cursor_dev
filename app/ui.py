"""
Gradio UI

ユーザーインターフェースを提供するモジュール
"""

from typing import Dict, Tuple

import gradio as gr

from .llm_processor import LLMProcessor, LLMProcessorError
from .search_engine import SearchEngine, SearchEngineError
from .twitter_client import TwitterClient, TwitterClientError


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

    def _format_tweet(self, tweet: Dict) -> str:
        """ツイートを表示用にフォーマット"""
        return f"""
        <div class="tweet-card">
            <div class="tweet-header">
                <span class="tweet-author">{tweet['author']}</span>
                <span class="tweet-date">{tweet['created_at']}</span>
            </div>
            <div class="tweet-body">
                {tweet['text']}
            </div>
            <div class="tweet-footer">
                <a href="{tweet['url']}" target="_blank">元のツイートを表示</a>
            </div>
        </div>
        """

    def _format_error(self, error: Exception) -> str:
        """エラーメッセージをフォーマット"""
        error_type = type(error).__name__
        if isinstance(error, (TwitterClientError, SearchEngineError, LLMProcessorError)):
            return f"""
            <div class="error-message">
                <h4>エラーが発生しました</h4>
                <p>{str(error)}</p>
                <p>対処方法:</p>
                <ul>
                    <li>入力内容を確認してください</li>
                    <li>しばらく待ってから再試行してください</li>
                    <li>問題が続く場合は管理者に連絡してください</li>
                </ul>
            </div>
            """
        return f"""
        <div class="error-message">
            <h4>システムエラー</h4>
            <p>予期せぬエラーが発生しました: {error_type}</p>
            <p>管理者に連絡してください</p>
        </div>
        """

    async def search_and_respond(
        self,
        query: str,
        top_k: int = 5,
        model_type: str = "gemini"
    ) -> Tuple[str, str]:
        """
        検索と回答生成を実行

        Args:
            query: 検索クエリ
            top_k: 取得する結果の数
            model_type: 使用するLLMの種類

        Returns:
            Tuple[str, str]: 生成された回答と検索結果のHTML
        """
        try:
            # 検索実行
            results = self.search_engine.search(query, top_k=top_k)
            
            # LLMで回答生成
            response = await self.llm_processor.generate_response(query, results)
            
            # 検索結果をHTML形式に整形
            results_html = "".join(self._format_tweet(tweet) for tweet in results)
            
            return response, results_html
        except Exception as e:
            error_html = self._format_error(e)
            return "", error_html

    def create_interface(self) -> gr.Blocks:
        """
        Gradioインターフェースを作成

        Returns:
            gr.Blocks: Gradioインターフェース
        """
        with gr.Blocks(
            title="X Bookmark RAG",
            css="""
                .tweet-card {
                    border: 1px solid #e1e8ed;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                    background: white;
                }
                .tweet-header {
                    margin-bottom: 8px;
                }
                .tweet-author {
                    font-weight: bold;
                    margin-right: 8px;
                }
                .tweet-date {
                    color: #657786;
                }
                .tweet-body {
                    margin: 8px 0;
                    line-height: 1.4;
                }
                .tweet-footer {
                    margin-top: 8px;
                }
                .tweet-footer a {
                    color: #1da1f2;
                    text-decoration: none;
                }
                .tweet-footer a:hover {
                    text-decoration: underline;
                }
                .error-message {
                    border: 1px solid #ffa4a4;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 16px 0;
                    background: #fff0f0;
                }
                .error-message h4 {
                    color: #d63031;
                    margin: 0 0 8px 0;
                }
                .error-message p {
                    margin: 8px 0;
                }
                .error-message ul {
                    margin: 8px 0;
                    padding-left: 24px;
                }
                .result-group {
                    border: 1px solid #e1e8ed;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 8px 0;
                    background: white;
                }
            """
        ) as interface:
            gr.Markdown("# X Bookmark RAG")
            gr.Markdown("Xのブックマークを検索し、AIが回答を生成します。")

            with gr.Row():
                with gr.Column():
                    query = gr.Textbox(
                        label="検索クエリ",
                        placeholder="検索したい内容を入力してください...",
                        lines=3
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
                    search_button = gr.Button("検索", variant="primary")

                with gr.Column():
                    with gr.Group(elem_classes=["result-group"]):
                        gr.Markdown("### AI回答")
                        response = gr.Markdown()
                    
                    with gr.Group(elem_classes=["result-group"]):
                        gr.Markdown("### 検索結果")
                        results = gr.HTML()

            search_button.click(
                fn=self.search_and_respond,
                inputs=[query, top_k, model_type],
                outputs=[response, results],
                api_name="search",
                show_progress="full"
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
