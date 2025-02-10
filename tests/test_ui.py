"""UIのテスト"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import gradio as gr
import pytest
from bs4 import BeautifulSoup

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


@pytest.mark.asyncio
async def test_input_validation(ui):
    """入力バリデーションのテスト"""
    # 空のクエリ
    response, results = await ui.search_and_respond("")
    assert response == ""
    assert "エラーが発生しました" in results
    assert "クエリが空です" in results

    # 長すぎるクエリ（1000文字）
    long_query = "a" * 1000
    response, results = await ui.search_and_respond(long_query)
    assert response == ""
    assert "エラーが発生しました" in results
    assert "クエリが長すぎます" in results

    # 無効なtop_k値
    response, results = await ui.search_and_respond("test", top_k=0)
    assert response == ""
    assert "エラーが発生しました" in results
    assert "結果数は1以上を指定してください" in results

    # 無効なモデルタイプ
    response, results = await ui.search_and_respond("test", model_type="invalid")
    assert response == ""
    assert "エラーが発生しました" in results
    assert "サポートされていないモデルタイプです" in results


@pytest.mark.asyncio
async def test_event_handlers(ui):
    """イベントハンドラのテスト"""
    interface = ui.create_interface()

    # 検索ボタンのクリックイベントを検証
    search_button = None
    for block in interface.blocks.values():
        if isinstance(block, gr.Button) and block.value == "検索":
            search_button = block
            break
    assert search_button is not None

    # イベントハンドラの設定を検証
    event_triggers = [fn.fn for fn in interface.fns]
    assert ui.search_and_respond in event_triggers

    # コンポーネントの接続を検証
    for fn in interface.fns:
        if fn.fn == ui.search_and_respond:
            assert len(fn.inputs) == 3  # query, top_k, model_type
            assert len(fn.outputs) == 2  # response, results
            assert fn.show_progress == "full"
            break


@pytest.mark.asyncio
async def test_component_state_changes(ui):
    """コンポーネントの状態変更のテスト"""
    interface = ui.create_interface()

    # インターフェースの存在を確認
    assert interface is not None
    assert isinstance(interface, gr.Blocks)

    # 検索中の状態変更をシミュレート
    with patch('gradio.Button.update') as mock_update:
        # 検索開始時
        await ui.search_and_respond("test")
        mock_update.assert_called_with(interactive=False)

        # 検索完了時
        mock_update.reset_mock()
        await ui.search_and_respond("test")
        mock_update.assert_called_with(interactive=True)

    # エラー時の状態をシミュレート
    ui.search_engine.search.side_effect = SearchEngineError("error")
    with patch('gradio.Markdown.update') as mock_update:
        await ui.search_and_respond("test")
        mock_update.assert_called()


def test_error_display_style(ui):
    """エラー表示のスタイルテスト"""
    # エラーメッセージのHTML生成
    error = SearchEngineError("test error")
    error_html = ui._format_error(error)

    # HTMLの解析
    soup = BeautifulSoup(error_html, 'html.parser')
    error_div = soup.find('div', class_='error-message')
    
    # スタイルの検証
    assert error_div is not None
    assert 'error-message' in error_div['class']
    assert error_div.find('h4') is not None
    assert error_div.find('p') is not None
    assert error_div.find('ul') is not None

    # エラータイプに応じたスタイルの違いを検証
    system_error = ValueError("system error")
    system_error_html = ui._format_error(system_error)
    soup = BeautifulSoup(system_error_html, 'html.parser')
    assert 'システムエラー' in soup.find('h4').text


@pytest.mark.asyncio
async def test_async_cancellation(ui):
    """非同期処理のキャンセルテスト"""
    # 長時間実行される処理をシミュレート
    async def slow_search(*args, **kwargs):
        await asyncio.sleep(10)
        return []
    ui.search_engine.search = slow_search

    # タスクの作成
    task = asyncio.create_task(ui.search_and_respond("test"))
    
    # 少し待ってからキャンセル
    await asyncio.sleep(0.1)
    task.cancel()

    # キャンセル時の動作を検証
    try:
        await task
    except asyncio.CancelledError:
        # キャンセルが正しく処理されることを確認
        pass
    else:
        pytest.fail("タスクがキャンセルされませんでした") 