"""大規模データセットのパフォーマンステスト"""

import time

import psutil
import pytest

from app.llm_processor import LLMProcessor
from app.search_engine import SearchEngine


@pytest.mark.performance
def test_search_engine_large_dataset(large_dataset):
    """SearchEngineの大規模データ処理テスト"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss

    engine = SearchEngine()

    # データ追加時のパフォーマンス計測
    start_time = time.time()
    engine.add_bookmarks(large_dataset)
    add_time = time.time() - start_time
    assert add_time < 300.0  # 5分以内にインデックス構築

    # メモリ使用量の確認
    current_memory = process.memory_info().rss
    memory_increase = (current_memory - initial_memory) / (1024 * 1024)  # MB
    assert memory_increase < 2000  # 2GB以内

    # 検索性能の確認
    start_time = time.time()
    results = engine.search("Python", top_k=10)
    search_time = time.time() - start_time
    assert search_time < 1.0  # 1秒以内に検索完了
    assert len(results) == 10


@pytest.mark.asyncio
@pytest.mark.performance
async def test_end_to_end_large_dataset(large_dataset):
    """エンドツーエンドの大規模データ処理テスト"""
    engine = SearchEngine()
    processor = LLMProcessor()

    # データ追加
    engine.add_bookmarks(large_dataset)

    # 検索からLLM応答までの一連の処理時間を計測
    start_time = time.time()
    search_results = engine.search("Python開発のベストプラクティス", top_k=5)
    response = await processor.generate_response(
        "Python開発のベストプラクティスについて教えてください", search_results
    )
    total_time = time.time() - start_time

    assert total_time < 10.0  # 10秒以内に完了
    assert isinstance(response, str)
    assert len(response) > 0
