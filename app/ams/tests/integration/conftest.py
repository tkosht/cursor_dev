"""Integration test configuration"""

import asyncio
import gc
import warnings

import pytest


@pytest.fixture(scope="function")
def event_loop():
    """Create a new event loop for each test function."""
    # 既存のループがあれば閉じる
    try:
        loop = asyncio.get_running_loop()
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass
    
    # 新しいループを作成
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    
    # テスト後のクリーンアップ
    # 残っているタスクを収集
    try:
        pending = asyncio.all_tasks(loop)
    except AttributeError:
        # Python 3.9+
        pending = asyncio.tasks.all_tasks(loop)
    
    # 現在のタスクを除外
    if pending:
        current = asyncio.current_task(loop)
        if current:
            pending.discard(current)
    
    # タスクをキャンセル
    for task in pending:
        task.cancel()
    
    # キャンセルしたタスクの完了を待つ
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    
    # gRPCのクリーンアップのために待機
    loop.run_until_complete(asyncio.sleep(0.5))
    
    # ループを閉じる
    loop.close()
    asyncio.set_event_loop(None)
    
    # ガベージコレクションを強制
    gc.collect()


@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """各テスト後のクリーンアップ"""
    # テスト実行
    yield
    
    # 非同期処理の完了を待つ
    await asyncio.sleep(0.2)
    
    # 警告を無視（gRPC関連の警告を抑制）
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited")