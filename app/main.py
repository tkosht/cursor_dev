"""
アプリケーションのエントリーポイント
"""

import os

from dotenv import load_dotenv

from .llm_processor import LLMProcessor
from .search_engine import SearchEngine
from .twitter_client import TwitterClient
from .ui import UI


def main():
    """アプリケーションのメインエントリーポイント"""
    # 環境変数の読み込み
    load_dotenv()

    # Twitterクライアントの初期化
    twitter_client = TwitterClient(
        api_key=os.getenv("TWITTER_API_KEY"),
        api_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )

    # 検索エンジンの初期化
    search_engine = SearchEngine()

    # LLMプロセッサの初期化
    llm_processor = LLMProcessor(
        model_type=os.getenv("LLM_MODEL_TYPE", "gemini"),
        api_key=os.getenv("LLM_API_KEY")
    )

    # UIの初期化と起動
    ui = UI(twitter_client, search_engine, llm_processor)
    ui.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main() 