"""UIのテスト"""

from unittest.mock import AsyncMock, MagicMock

import gradio as gr
import pytest

from app.llm_processor import LLMProcessorError
from app.search_engine import SearchEngineError
from app.ui import UI


@pytest.fixture
def ui():
    """UIインスタンスを作成"""
    twitter_client = MagicMock()
    search_engine = MagicMock()
    llm_processor = MagicMock()
    llm_processor.generate_response = AsyncMock()
    return UI(twitter_client, search_engine, llm_processor)


def test_format_tweet(ui):
    """ツイートのフォーマットテスト"""
    tweet = {
        "author": "test_user",
        "created_at": "2024-03-21",
        "text": "test tweet",
        "url": "https://twitter.com/test"
    }
    formatted = ui._format_tweet(tweet)
    assert "test_user" in formatted
    assert "2024-03-21" in formatted
    assert "test tweet" in formatted
    assert "https://twitter.com/test" in formatted


def test_format_error_known_error(ui):
    """既知のエラーフォーマットテスト"""
    error = SearchEngineError("test error")
    formatted = ui._format_error(error)
    assert "エラーが発生しました" in formatted
    assert "test error" in formatted


def test_format_error_unknown_error(ui):
    """未知のエラーフォーマットテスト"""
    error = ValueError("test error")
    formatted = ui._format_error(error)
    assert "システムエラー" in formatted
    assert "ValueError" in formatted


@pytest.mark.asyncio
async def test_search_and_respond_success(ui):
    """検索と回答生成の成功テスト"""
    # モックの設定
    ui.search_engine.search.return_value = [
        {
            "author": "test_user",
            "created_at": "2024-03-21",
            "text": "test tweet",
            "url": "https://twitter.com/test"
        }
    ]
    ui.llm_processor.generate_response.return_value = "test response"

    # テスト実行
    response, results = await ui.search_and_respond("test query")

    # 検証
    assert response == "test response"
    assert "test tweet" in results
    ui.search_engine.search.assert_called_once_with("test query", top_k=5)
    ui.llm_processor.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_search_and_respond_search_error(ui):
    """検索エラー時のテスト"""
    # モックの設定
    ui.search_engine.search.side_effect = SearchEngineError("search error")

    # テスト実行
    response, results = await ui.search_and_respond("test query")

    # 検証
    assert response == ""
    assert "エラーが発生しました" in results
    assert "search error" in results


@pytest.mark.asyncio
async def test_search_and_respond_llm_error(ui):
    """LLMエラー時のテスト"""
    # モックの設定
    ui.search_engine.search.return_value = [
        {
            "author": "test_user",
            "created_at": "2024-03-21",
            "text": "test tweet",
            "url": "https://twitter.com/test"
        }
    ]
    ui.llm_processor.generate_response.side_effect = LLMProcessorError("llm error")

    # テスト実行
    response, results = await ui.search_and_respond("test query")

    # 検証
    assert response == ""
    assert "エラーが発生しました" in results
    assert "llm error" in results


def test_create_interface(ui):
    """インターフェース作成のテスト"""
    # インターフェース作成
    interface = ui.create_interface()

    # 検証
    assert isinstance(interface, gr.Blocks)
    # インターフェースの構造を検証
    assert interface.title == "X Bookmark RAG"  # タイトルが設定されていることを確認
    assert interface.css is not None  # CSSが設定されていることを確認
    assert len(interface.blocks) > 0  # コンポーネントが存在することを確認
    assert len(interface.fns) > 0  # イベントハンドラが設定されていることを確認

    # コンポーネントの種類を検証
    component_types = [type(comp) for comp in interface.blocks.values()]
    assert gr.Textbox in component_types  # 検索入力欄
    assert gr.Slider in component_types  # 結果数選択
    assert gr.Dropdown in component_types  # モデル選択
    assert gr.Button in component_types  # 検索ボタン
    assert gr.Markdown in component_types  # 回答表示
    assert gr.HTML in component_types  # 結果表示 