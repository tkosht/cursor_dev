"""UIとSearchEngineの統合テスト"""

import os
import shutil
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.llm_processor import LLMProcessor
from app.search_engine import SearchEngine, SearchEngineError
from app.twitter_client import TwitterClient
from app.ui import UI


@pytest.fixture
def temp_dir():
    """一時ディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # テスト後にディレクトリを削除
    shutil.rmtree(temp_dir)


@pytest.fixture
def index_dir(temp_dir):
    """検索エンジンのインデックスディレクトリ"""
    return os.path.join(temp_dir, "search_index")


@pytest.fixture
def sample_bookmarks():
    """テスト用のサンプルブックマーク"""
    return [
        {
            "id": "1",
            "url": "https://twitter.com/user1/status/1",
            "text": "Pythonプログラミングについて",
            "created_at": "1234567890",
            "author": "user1",
        },
        {
            "id": "2",
            "url": "https://twitter.com/user2/status/2",
            "text": "機械学習の基礎",
            "created_at": "1234567891",
            "author": "user2",
        },
        {
            "id": "3",
            "url": "https://twitter.com/user3/status/3",
            "text": "データ分析の手法",
            "created_at": "1234567892",
            "author": "user3",
        },
    ]


@pytest.fixture
def search_engine(index_dir):
    """SearchEngineインスタンス"""
    return SearchEngine(index_dir=index_dir)


@pytest.fixture
def twitter_client():
    """TwitterClientのモックインスタンス"""
    return Mock(spec=TwitterClient)


@pytest.fixture
def llm_processor():
    """LLMProcessorのモックインスタンス"""
    mock_processor = Mock(spec=LLMProcessor)
    mock_processor.SUPPORTED_MODELS = {
        "gemini": "gemini-pro",
        "gpt": "gpt-4-turbo-preview",
        "claude": "claude-3-sonnet-20240229",
        "ollama": "mistral",
    }
    mock_processor.generate_response = AsyncMock()
    return mock_processor


@pytest.fixture
def mock_gradio_components():
    """Gradioコンポーネントのモック"""
    with patch("gradio.Blocks") as mock_blocks, \
         patch("gradio.Textbox") as mock_textbox, \
         patch("gradio.Slider") as mock_slider, \
         patch("gradio.Dropdown") as mock_dropdown, \
         patch("gradio.Button") as mock_button, \
         patch("gradio.Markdown") as mock_markdown, \
         patch("gradio.HTML") as mock_html:
        
        mock_blocks.return_value.__enter__.return_value = mock_blocks
        mock_blocks.return_value.__exit__.return_value = None
        mock_blocks.blocks = {}

        yield {
            "blocks": mock_blocks,
            "textbox": mock_textbox,
            "slider": mock_slider,
            "dropdown": mock_dropdown,
            "button": mock_button,
            "markdown": mock_markdown,
            "html": mock_html,
        }


@pytest.fixture
def ui(search_engine, twitter_client, llm_processor, mock_gradio_components):
    """UIインスタンス"""
    return UI(
        twitter_client=twitter_client,
        search_engine=search_engine,
        llm_processor=llm_processor
    )


@pytest.mark.asyncio
async def test_basic_integration_flow(ui, search_engine, sample_bookmarks):
    """基本的な統合フローのテスト"""
    # SearchEngineにブックマークを追加
    search_engine.add_bookmarks(sample_bookmarks)

    # LLMの応答をモック
    ui.llm_processor.generate_response.return_value = "Pythonはプログラミング言語です。"

    # 検索と回答生成
    response, results = await ui.search_and_respond("Python")

    # 検証
    assert isinstance(response, str)
    assert "Python" in response
    assert isinstance(results, str)
    assert "user1" in results
    assert "Pythonプログラミング" in results


@pytest.mark.asyncio
async def test_search_error(ui, search_engine):
    """検索エラー時の動作確認"""
    with patch.object(
        search_engine, "search", side_effect=SearchEngineError("検索エラー")
    ):
        response, results = await ui.search_and_respond("Python")
        assert response == ""
        assert "エラーが発生しました" in results
        assert "検索エラー" in results


@pytest.mark.asyncio
async def test_empty_query(ui):
    """空のクエリの処理確認"""
    response, results = await ui.search_and_respond("")
    assert response == ""
    assert "エラーが発生しました" in results
    assert "クエリが空です" in results


@pytest.mark.asyncio
async def test_long_query(ui):
    """長すぎるクエリの処理確認"""
    long_query = "あ" * 1000
    response, results = await ui.search_and_respond(long_query)
    assert response == ""
    assert "エラーが発生しました" in results
    assert "クエリが長すぎます" in results


@pytest.mark.asyncio
async def test_invalid_top_k(ui):
    """無効なtop_k値の処理確認"""
    response, results = await ui.search_and_respond("Python", top_k=0)
    assert response == ""
    assert "エラーが発生しました" in results
    assert "結果数は1以上を指定してください" in results


@pytest.mark.asyncio
async def test_invalid_model_type(ui):
    """無効なモデルタイプの処理確認"""
    response, results = await ui.search_and_respond(
        "Python", model_type="invalid"
    )
    assert response == ""
    assert "エラーが発生しました" in results
    assert "サポートされていないモデルタイプです" in results


@pytest.mark.asyncio
async def test_interface_creation(ui, mock_gradio_components):
    """インターフェース作成の確認"""
    interface = ui.create_interface()

    # インターフェースの構造を検証
    assert isinstance(interface, mock_gradio_components["blocks"].__class__)
    assert interface.title == "X Bookmark RAG"
    assert interface.css is not None

    # コンポーネントの存在を確認
    assert mock_gradio_components["textbox"].called  # 検索入力欄
    assert mock_gradio_components["slider"].called  # 結果数選択
    assert mock_gradio_components["dropdown"].called  # モデル選択
    assert mock_gradio_components["button"].called  # 検索ボタン
    assert mock_gradio_components["markdown"].called  # 回答表示
    assert mock_gradio_components["html"].called  # 結果表示


@pytest.mark.asyncio
async def test_component_state_changes(ui, search_engine, sample_bookmarks, mock_gradio_components):
    """コンポーネントの状態変更の確認"""
    search_engine.add_bookmarks(sample_bookmarks)

    # LLMの応答をモック
    ui.llm_processor.generate_response.return_value = "テスト回答"

    # 検索ボタンの状態変更をシミュレート
    mock_button = mock_gradio_components["button"].return_value
    mock_button.update = Mock()

    # 検索開始時
    await ui.search_and_respond("Python")
    mock_button.update.assert_called_with(interactive=False)

    # 検索完了時
    mock_button.update.reset_mock()
    await ui.search_and_respond("Python")
    mock_button.update.assert_called_with(interactive=True)


@pytest.mark.asyncio
async def test_error_display(ui, mock_gradio_components):
    """エラー表示の確認"""
    # エラーメッセージの表示をシミュレート
    mock_markdown = mock_gradio_components["markdown"].return_value
    mock_markdown.update = Mock()

    response, results = await ui.search_and_respond("")
    mock_markdown.update.assert_called()
    assert "エラーが発生しました" in results


@pytest.mark.asyncio
async def test_concurrent_searches(ui, search_engine, sample_bookmarks):
    """並行検索の処理確認"""
    import asyncio

    search_engine.add_bookmarks(sample_bookmarks)

    # LLMの応答をモック
    ui.llm_processor.generate_response.side_effect = lambda query, *args: f"回答: {query}"

    # 5つの並行検索を実行
    queries = ["Python", "機械学習", "データ分析", "プログラミング", "AI"]
    tasks = [ui.search_and_respond(query) for query in queries]
    results = await asyncio.gather(*tasks)

    # 結果を検証
    for (response, result), query in zip(results, queries):
        assert f"回答: {query}" in response
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_memory_usage(ui, search_engine):
    """メモリ使用量の確認"""
    import psutil

    process = psutil.Process()

    # 大規模データセットを生成
    large_bookmarks = [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": f"テストツイート {i} " * 100,  # 長めのテキスト
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(1000)
    ]

    # メモリ使用量を測定
    initial_memory = process.memory_info().rss

    # 検索と回答生成
    search_engine.add_bookmarks(large_bookmarks)
    ui.llm_processor.generate_response.return_value = "テスト回答"
    await ui.search_and_respond("テスト")

    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB単位

    assert memory_increase < 2000  # メモリ増加は2GB以内


@pytest.mark.asyncio
async def test_response_format(ui, search_engine, sample_bookmarks):
    """レスポンス形式の確認"""
    search_engine.add_bookmarks(sample_bookmarks)

    # LLMの応答をモック
    ui.llm_processor.generate_response.return_value = "テスト回答"

    response, results = await ui.search_and_respond("Python")

    # 回答形式の検証
    assert isinstance(response, str)
    assert response == "テスト回答"

    # 結果表示形式の検証
    assert isinstance(results, str)
    assert "user1" in results
    assert "Python" in results
    assert "https://twitter.com" in results
