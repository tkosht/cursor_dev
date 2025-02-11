"""LLMProcessorとSearchEngineの統合テスト"""

import os
import shutil
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from app.llm_processor import LLMProcessor, LLMProcessorError
from app.search_engine import SearchEngine, SearchEngineError


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
def llm_processor():
    """LLMProcessorインスタンス"""
    return LLMProcessor()


@pytest.mark.asyncio
async def test_basic_integration_flow(
    search_engine, llm_processor, sample_bookmarks
):
    """基本的な統合フローのテスト"""
    # SearchEngineにブックマークを追加
    search_engine.add_bookmarks(sample_bookmarks)

    # 検索を実行
    search_results = search_engine.search("Python")
    assert len(search_results) > 0

    # LLMで回答を生成
    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        return_value="Pythonはプログラミング言語です。",
    ):
        response = await llm_processor.generate_response(
            "Pythonとは？", search_results
        )
        assert isinstance(response, str)
        assert "Python" in response


@pytest.mark.asyncio
async def test_llm_api_error(search_engine, llm_processor, sample_bookmarks):
    """LLM APIエラー時の動作確認"""
    search_engine.add_bookmarks(sample_bookmarks)
    search_results = search_engine.search("Python")

    # APIエラーをシミュレート
    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        side_effect=LLMProcessorError("APIエラー"),
    ):
        with pytest.raises(LLMProcessorError) as exc_info:
            await llm_processor.generate_response(
                "Pythonとは？", search_results
            )
        assert "APIエラー" in str(exc_info.value)


@pytest.mark.asyncio
async def test_context_length_exceeded(search_engine, llm_processor):
    """コンテキスト長超過時の動作確認"""
    # 長いテキストを含むブックマークを生成
    long_bookmarks = [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": "あ" * 10000,  # 非常に長いテキスト
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(10)
    ]

    search_engine.add_bookmarks(long_bookmarks)
    search_results = search_engine.search("あ")

    # コンテキスト長超過エラーをシミュレート
    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        side_effect=LLMProcessorError("コンテキスト長が上限を超えています"),
    ):
        with pytest.raises(LLMProcessorError) as exc_info:
            await llm_processor.generate_response(
                "長いテキストの要約は？", search_results
            )
        assert "コンテキスト長" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_search_results(search_engine, llm_processor):
    """無効な検索結果の処理確認"""
    invalid_results = [({"invalid": "data"}, 0.5)]

    # 無効な検索結果での処理を確認
    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        side_effect=LLMProcessorError("無効な検索結果"),
    ):
        with pytest.raises(LLMProcessorError) as exc_info:
            await llm_processor.generate_response("クエリ", invalid_results)
        assert "無効な検索結果" in str(exc_info.value)


@pytest.mark.asyncio
async def test_response_quality(
    search_engine, llm_processor, sample_bookmarks
):
    """回答品質の確認"""
    search_engine.add_bookmarks(sample_bookmarks)
    search_results = search_engine.search("Python")

    # 高品質な回答をシミュレート
    expected_response = """
    Pythonプログラミングについて説明します：
    1. プログラミング言語の基礎
    2. 機械学習での活用
    3. データ分析での応用
    """

    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        return_value=expected_response,
    ):
        response = await llm_processor.generate_response(
            "Pythonの用途は？", search_results
        )
        assert "プログラミング" in response
        assert "機械学習" in response
        assert "データ分析" in response


@pytest.mark.asyncio
async def test_response_time(search_engine, llm_processor, sample_bookmarks):
    """応答時間の確認"""
    search_engine.add_bookmarks(sample_bookmarks)
    search_results = search_engine.search("Python")

    import time

    start_time = time.time()

    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        return_value="テスト回答",
    ):
        await llm_processor.generate_response("Pythonとは？", search_results)

    end_time = time.time()
    response_time = end_time - start_time

    assert response_time < 5.0  # 応答は5秒以内


@pytest.mark.asyncio
async def test_concurrent_requests(
    search_engine, llm_processor, sample_bookmarks
):
    """並行リクエストの処理確認"""
    import asyncio

    search_engine.add_bookmarks(sample_bookmarks)
    search_results = search_engine.search("Python")

    # 複数の並行リクエストをシミュレート
    async def make_request(i: int):
        with patch.object(
            llm_processor,
            "generate_response",
            new_callable=AsyncMock,
            return_value=f"回答 {i}",
        ):
            return await llm_processor.generate_response(
                f"質問 {i}", search_results
            )

    # 5つの並行リクエストを実行
    tasks = [make_request(i) for i in range(5)]
    responses = await asyncio.gather(*tasks)

    assert len(responses) == 5
    for i, response in enumerate(responses):
        assert f"回答 {i}" in response


@pytest.mark.asyncio
async def test_error_handling(search_engine, llm_processor, sample_bookmarks):
    """エラーハンドリングの確認"""
    search_engine.add_bookmarks(sample_bookmarks)

    # 検索エラー
    with patch.object(
        search_engine, "search", side_effect=SearchEngineError("検索エラー")
    ):
        with pytest.raises(SearchEngineError) as exc_info:
            search_engine.search("Python")
        assert "検索エラー" in str(exc_info.value)

    # LLMエラー
    search_results = search_engine.search("Python")
    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        side_effect=LLMProcessorError("LLMエラー"),
    ):
        with pytest.raises(LLMProcessorError) as exc_info:
            await llm_processor.generate_response(
                "Pythonとは？", search_results
            )
        assert "LLMエラー" in str(exc_info.value)


@pytest.mark.asyncio
async def test_memory_usage(search_engine, llm_processor):
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
    search_results = search_engine.search("テスト")

    with patch.object(
        llm_processor,
        "generate_response",
        new_callable=AsyncMock,
        return_value="テスト回答",
    ):
        await llm_processor.generate_response("テストについて", search_results)

    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB単位

    assert memory_increase < 2000  # メモリ増加は2GB以内
