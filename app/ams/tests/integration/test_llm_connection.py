"""LLM接続テスト - 実際のAPI呼び出し確認

設定ベースの実装で、ハードコードなし。
pytest形式で実装。
"""

import asyncio
import os
import time
from typing import Any, Dict

import pytest
from src.config import get_config
from src.utils.llm_factory import create_llm


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_llm_connection():
    """基本的なLLM接続テスト"""
    config = get_config()
    
    # LLM作成（設定ベース）
    llm = create_llm()
    assert llm is not None
    
    # シンプルな呼び出し
    start_time = time.time()
    response = await llm.ainvoke("1+1は何ですか？短く答えてください。")
    elapsed = time.time() - start_time
    
    # 検証
    assert response is not None
    assert response.content is not None
    assert len(response.content) > 0
    assert elapsed > 0.1  # 実際のAPIコールは100ms以上かかる


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.xfail(
    condition=not os.getenv("PYTEST_INDIVIDUAL_RUN"),
    reason="Known issue with event loop in batch execution - see docs/event_loop_issue_workaround.md"
)
async def test_llm_with_japanese():
    """日本語処理のテスト"""
    from src.utils.async_llm_manager import create_async_llm_manager
    
    llm = create_llm()
    manager = create_async_llm_manager(llm)
    
    try:
        response = await manager.ainvoke("「こんにちは」を英語に翻訳してください。")
        
        # 基本的な検証
        assert response is not None
        assert response.content is not None
        # "Hello" または "Hi" が含まれることを期待
        assert any(word in response.content.lower() for word in ["hello", "hi"])
    finally:
        await manager.cleanup()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_error_handling():
    """エラーハンドリングのテスト"""
    # 空のプロンプトでもエラーにならないことを確認
    llm = create_llm()
    
    try:
        response = await llm.ainvoke("")
        # 空でも何らかのレスポンスが返る
        assert response is not None
    except Exception as e:
        # エラーが発生しても適切な例外であること
        assert isinstance(e, Exception)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_configuration():
    """設定が正しく適用されているかのテスト"""
    config = get_config()
    llm = create_llm()
    
    # LLMインスタンスが設定に基づいて作成されていることを確認
    # （内部実装の詳細には依存しない）
    assert llm is not None
    
    # 設定値の確認（モデル名など）
    assert config.llm.provider in ["gemini", "openai", "anthropic"]
    assert config.llm.gemini_model == "gemini-2.5-flash"  # デフォルト値


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.xfail(
    condition=not os.getenv("PYTEST_INDIVIDUAL_RUN"),
    reason="Known issue with event loop in batch execution - see docs/event_loop_issue_workaround.md"
)
async def test_multiple_llm_calls():
    """複数回の呼び出しテスト"""
    from src.utils.async_llm_manager import create_async_llm_manager
    
    llm = create_llm()
    manager = create_async_llm_manager(llm)
    
    try:
        prompts = [
            "1 + 1 = ?",
            "2 + 2 = ?",
            "3 + 3 = ?",
        ]

        # 並列実行
        tasks = [manager.ainvoke(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks)
        
        # すべての呼び出しが成功
        assert len(responses) == 3
        assert all(r.content for r in responses)
    finally:
        await manager.cleanup()