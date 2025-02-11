"""長期安定性テスト"""

import asyncio
import time

import psutil
import pytest

from app.llm_processor import LLMProcessor
from app.search_engine import SearchEngine


@pytest.mark.stability
def test_memory_leak_search_engine(large_dataset):
    """SearchEngineのメモリリーク検出テスト"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    engine = SearchEngine()

    # 100回の検索操作を実行
    for i in range(100):
        engine.add_bookmarks(large_dataset[:1000])  # 1000件ずつ追加
        _ = engine.search("Python", top_k=5)  # 結果は使用しないが、処理は必要
        engine.clear()  # インデックスをクリア

    # メモリ使用量を確認
    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
    assert memory_increase < 100  # 長期実行後も100MB以内の増加に抑える


@pytest.mark.asyncio
@pytest.mark.stability
async def test_continuous_operation(large_dataset):
    """1時間の継続的な操作テスト"""
    engine = SearchEngine()
    processor = LLMProcessor()
    engine.add_bookmarks(large_dataset)

    start_time = time.time()
    error_count = 0
    operation_count = 0

    # 1時間の継続的な操作
    while time.time() - start_time < 3600:  # 1時間
        try:
            # 検索とLLM処理を実行
            results = engine.search("Python", top_k=5)
            _ = await processor.generate_response(  # 結果は使用しないが、処理は必要
                "Pythonについて説明してください", results
            )
            operation_count += 1

            # 10秒間隔で実行
            await asyncio.sleep(10)

        except Exception as e:
            error_count += 1
            print(f"エラー発生: {e}")

    # エラー率を確認
    error_rate = error_count / operation_count
    assert error_rate < 0.01  # エラー率1%未満
