"""同時リクエスト処理のパフォーマンステスト"""

import asyncio
import time

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
        "ウェブ開発フレームワーク",
        "APIデザイン",
        "テスト駆動開発",
        "マイクロサービス",
        "コンテナ化",
        "CI/CD",
        "セキュリティベストプラクティス",
    ]


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_search_requests(concurrent_queries, large_dataset):
    """検索の同時リクエスト処理テスト"""
    engine = SearchEngine()
    engine.add_bookmarks(large_dataset)

    start_time = time.time()

    # 10件の同時検索リクエスト
    tasks = [
        asyncio.create_task(asyncio.to_thread(engine.search, query, top_k=5))
        for query in concurrent_queries
    ]

    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    assert total_time < 10.0  # 10秒以内に全リクエスト完了
    assert len(results) == len(concurrent_queries)
    assert all(len(r) == 5 for r in results)


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_llm_requests(concurrent_queries, large_dataset):
    """LLM処理の同時リクエスト処理テスト"""
    engine = SearchEngine()
    processor = LLMProcessor()
    engine.add_bookmarks(large_dataset)

    # 検索結果を準備
    search_results = [
        engine.search(query, top_k=3) for query in concurrent_queries
    ]

    start_time = time.time()

    # 10件の同時LLMリクエスト
    tasks = [
        processor.generate_response(
            f"{query}について説明してください", results
        )
        for query, results in zip(concurrent_queries, search_results)
    ]

    responses = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    assert total_time < 30.0  # 30秒以内に全リクエスト完了
    assert len(responses) == len(concurrent_queries)
    assert all(isinstance(r, str) for r in responses)
