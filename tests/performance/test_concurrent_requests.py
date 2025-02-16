"""同時リクエスト処理のパフォーマンステスト"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock

import pytest

from app.llm_processor import LLMProcessor
from app.search_engine import SearchEngine


@pytest.fixture
def concurrent_queries():
    """同時実行用のクエリセット"""
    return [
        "Pythonプログラミング",
        "機械学習入門",
        "データ分析手法",
        "ウェブ開発",
        "API設計",
    ]


@pytest.fixture
def mock_llm_processor():
    """LLMProcessorのモックインスタンス"""
    mock_processor = Mock(spec=LLMProcessor)
    mock_processor.SUPPORTED_MODELS = {
        "gemini": "gemini-pro",
        "gpt": "gpt-4-turbo-preview",
        "claude": "claude-3-sonnet-20240229",
        "ollama": "mistral",
    }
    mock_processor.generate_response = AsyncMock(
        side_effect=lambda query, *args: f"回答: {query}"
    )
    return mock_processor


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_search_requests(concurrent_queries, large_dataset, mock_transformer):
    """検索の同時リクエスト処理テスト"""
    engine = SearchEngine(use_gpu=False)
    engine.add_bookmarks(large_dataset)

    start_time = time.time()

    # 5件の同時検索リクエスト
    tasks = [
        asyncio.create_task(asyncio.to_thread(engine.search, query, top_k=5))
        for query in concurrent_queries
    ]

    # タイムアウトを設定（5秒）
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
        total_time = time.time() - start_time

        assert total_time < 5.0  # 5秒以内に全リクエスト完了
        assert len(results) == len(concurrent_queries)
        assert all(len(r) <= 5 for r in results)
    except asyncio.TimeoutError:
        pytest.fail("テストがタイムアウトしました（5秒）")


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_llm_requests(concurrent_queries, large_dataset, mock_llm_processor, mock_transformer):
    """LLM処理の同時リクエスト処理テスト"""
    engine = SearchEngine(use_gpu=False)
    engine.add_bookmarks(large_dataset)

    # 検索結果を準備
    search_results = [
        engine.search(query, top_k=3) for query in concurrent_queries
    ]

    start_time = time.time()

    # 5件の同時LLMリクエスト
    tasks = [
        mock_llm_processor.generate_response(
            f"{query}について説明してください", results
        )
        for query, results in zip(concurrent_queries, search_results)
    ]

    try:
        responses = await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
        total_time = time.time() - start_time

        assert total_time < 5.0  # 5秒以内に全リクエスト完了
        assert len(responses) == len(concurrent_queries)
        assert all(isinstance(r, str) for r in responses)
    except asyncio.TimeoutError:
        pytest.fail("テストがタイムアウトしました（5秒）")


@pytest.mark.asyncio
@pytest.mark.performance
async def test_mixed_workload(concurrent_queries, large_dataset, mock_llm_processor, mock_transformer):
    """検索とLLM処理の混合ワークロードテスト"""
    engine = SearchEngine(use_gpu=False)
    engine.add_bookmarks(large_dataset)

    start_time = time.time()

    # 検索タスク（3件）とLLMタスク（2件）を同時実行
    search_tasks = [
        asyncio.create_task(asyncio.to_thread(engine.search, query, top_k=5))
        for query in concurrent_queries[:3]
    ]

    # 事前に検索結果を準備（LLMタスク用）
    llm_search_results = [
        engine.search(query, top_k=3) for query in concurrent_queries[3:]
    ]

    llm_tasks = [
        mock_llm_processor.generate_response(
            f"{query}について説明してください", results
        )
        for query, results in zip(concurrent_queries[3:], llm_search_results)
    ]

    # 全タスクを同時実行
    all_tasks = search_tasks + llm_tasks
    try:
        results = await asyncio.wait_for(asyncio.gather(*all_tasks), timeout=5.0)
        total_time = time.time() - start_time

        # 検索結果（前半3件）とLLM応答（後半2件）を検証
        search_results = results[:3]
        llm_responses = results[3:]

        assert total_time < 5.0  # 5秒以内に全リクエスト完了
        assert all(len(r) <= 5 for r in search_results)  # 検索結果の件数確認
        assert all(isinstance(r, str) for r in llm_responses)  # LLM応答の型確認
    except asyncio.TimeoutError:
        pytest.fail("テストがタイムアウトしました（5秒）")
