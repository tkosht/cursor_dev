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

    # 10回の検索操作を実行
    for i in range(10):
        engine.add_bookmarks(large_dataset[:10000])  # 10000件ずつ追加
        _ = engine.search("Python", top_k=5)  # 結果は使用しないが、処理は必要
        engine.clear()  # インデックスをクリア

    # メモリ使用量を確認
    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
    assert memory_increase < 100  # 長期実行後も100MB以内の増加に抑える


@pytest.mark.stability
def test_resource_usage_monitoring(large_dataset):
    """リソース使用量の監視テスト"""
    process = psutil.Process()
    engine = SearchEngine()
    engine.add_bookmarks(large_dataset)

    # 初期状態の記録
    initial_memory = process.memory_info().rss
    initial_io = process.io_counters()

    # 1分間の連続処理
    start_time = time.time()
    operation_count = 0
    peak_cpu = 0
    peak_memory = 0

    while time.time() - start_time < 60:  # 1分間
        # 検索処理を実行
        _ = engine.search("Python", top_k=5)
        operation_count += 1

        # リソース使用量を記録
        cpu_percent = process.cpu_percent()
        current_memory = process.memory_info().rss
        peak_cpu = max(peak_cpu, cpu_percent)
        peak_memory = max(peak_memory, current_memory)

        time.sleep(1)  # 1秒間隔で実行

    # 最終状態の記録
    final_io = process.io_counters()

    # リソース使用量の検証
    memory_increase = (peak_memory - initial_memory) / (1024 * 1024)  # MB
    io_read = (final_io.read_bytes - initial_io.read_bytes) / (1024 * 1024)  # MB
    io_write = (final_io.write_bytes - initial_io.write_bytes) / (1024 * 1024)  # MB

    assert peak_cpu < 80.0  # CPU使用率80%未満
    assert memory_increase < 1000  # メモリ増加1GB未満
    assert io_read < 100  # 読み込み100MB未満
    assert io_write < 100  # 書き込み100MB未満
    assert operation_count > 500  # 1分間で500回以上の操作


@pytest.mark.asyncio
@pytest.mark.stability
async def test_continuous_operation(large_dataset):
    """5分間の継続的な操作テスト"""
    engine = SearchEngine()
    processor = LLMProcessor()
    engine.add_bookmarks(large_dataset)

    start_time = time.time()
    error_count = 0
    operation_count = 0

    # 5分間の継続的な操作
    while time.time() - start_time < 300:  # 5分間
        try:
            # 検索とLLM処理を実行
            results = engine.search("Python", top_k=5)
            _ = await processor.generate_response(  # 結果は使用しないが、処理は必要
                "Pythonについて説明してください", results
            )
            operation_count += 1

            # 30秒間隔でLLM処理を実行
            if operation_count % 3 == 0:
                results = engine.search("Python", top_k=5)
                _ = await processor.generate_response(  # 結果は使用しないが、処理は必要
                    "Pythonについて説明してください", results
                )

            # 10秒間隔で実行
            await asyncio.sleep(10)

        except Exception as e:
            error_count += 1
            print(f"エラー発生: {e}")

    # エラー率を確認
    error_rate = error_count / operation_count
    assert error_rate < 0.01  # エラー率1%未満
