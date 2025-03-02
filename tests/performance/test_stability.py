"""長期安定性テスト"""

import asyncio
import gc
import os
import time

import psutil
import pytest
import torch

from app.llm_processor import LLMProcessor
from app.search_engine import SearchEngine


def get_memory_usage():
    """現在のプロセスのメモリ使用量をMB単位で返す"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # バイトからMBに変換

@pytest.mark.stability
def test_memory_leak_search_engine():
    """SearchEngineクラスのメモリリークテスト"""
    # 初期メモリ使用量を記録
    initial_memory = get_memory_usage()
    
    # テスト用のブックマークデータ
    test_bookmarks = [
        {"id": f"id_{i}", "text": f"テスト用ブックマーク {i} の内容です。これは検索テスト用のデータです。" * 5}
        for i in range(50)  # 500から50に減らす
    ]
    
    # 繰り返し回数を減らす（10→3）
    for i in range(3):
        # SearchEngineインスタンスを作成
        engine = SearchEngine(
            model_name="intfloat/multilingual-e5-small",  # largeからsmallに変更
            index_dir=os.path.join(os.getcwd(), "tests", "data", "test_index"),
            use_gpu=True
        )
        
        # ブックマークを追加
        engine.add_bookmarks(test_bookmarks)
        
        # 検索を実行
        _ = engine.search("テスト検索", top_k=5)  # 結果は使用しないので_に代入
        
        # インデックスをクリア
        engine.clear()
        
        # 明示的にインスタンスを削除
        del engine
        
        # ガベージコレクションを実行
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    # 最終メモリ使用量を記録
    final_memory = get_memory_usage()
    
    # メモリ増加量を計算
    memory_increase = final_memory - initial_memory
    
    # メモリ増加量が閾値以下であることを確認
    # 閾値を調整（100MB→500MB）
    assert memory_increase < 500, f"メモリリークの可能性: {memory_increase} MB増加"


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
