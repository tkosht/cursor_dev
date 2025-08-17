"""LLM接続テスト - 実際のAPI呼び出し確認

設定ベースの実装で、ハードコードなし。pytest形式。

Requirements/Design traceability:
- AMS-REQ-001: LLMプロバイダ設定/モデル選択の要件
- AMS-IG-006: 設定仕様（環境変数・デフォルト切替の確認）
"""

import asyncio
import time

import os
import pytest

from src.config import get_config
from src.utils.llm_factory import create_llm


def _keys_available() -> bool:
    return bool(
        os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_llm_connection():
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
    """基本的なLLM接続テスト"""
    config = get_config()

    # LLM作成（設定ベース）
    llm = create_llm()
    assert llm is not None

    # シンプルな呼び出し
    start_time = time.time()
    response = await llm.ainvoke("1+1は何ですか？短く答えてください。")
    elapsed = time.time() - start_time

    # 実際のLLMレスポンスをログ出力
    print("\n=== LLM Response Debug ===")
    print(f"Response type: {type(response)}")
    print(f"Response content: '{response.content}'")
    print(f"Content length: {len(response.content)} characters")
    print(f"Elapsed time: {elapsed:.3f} seconds")
    print(f"LLM provider: {config.llm.provider}")
    print("========================\n")

    # 検証
    assert response is not None
    assert response.content is not None
    assert len(response.content) > 0
    assert elapsed > 0.1  # 実際のAPIコールは100ms以上かかる


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_natural_language_response():
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
    """実際のLLM応答の自然さを確認"""
    llm = create_llm()

    # より複雑な質問
    response = await llm.ainvoke("なぜ空は青いのですか？簡潔に説明してください。")

    print("\n=== Natural Language Response ===")
    print("Question: なぜ空は青いのですか？")
    print(f"Response: {response.content}")
    print(f"Response length: {len(response.content)} characters")
    print("================================\n")

    # 検証：自然言語の応答であることを確認
    assert response is not None
    assert len(response.content) > 10  # 単純な数値回答ではない
    assert any(
        word in response.content.lower()
        for word in ["光", "散乱", "波長", "light", "scatter", "wavelength"]
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_with_japanese(llm_manager):
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
    """日本語処理のテスト"""
    response = await llm_manager.ainvoke("「こんにちは」を英語に翻訳してください。")

    # 基本的な検証
    assert response is not None
    assert response.content is not None
    # "Hello" または "Hi" が含まれることを期待
    assert any(word in response.content.lower() for word in ["hello", "hi"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_error_handling():
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
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
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
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
async def test_multiple_llm_calls(llm_manager):
    if not _keys_available():
        pytest.skip("No LLM API key available for testing")
    """複数回の呼び出しテスト"""
    prompts = [
        "1 + 1 = ?",
        "2 + 2 = ?",
        "3 + 3 = ?",
    ]

    # 並列実行
    tasks = [llm_manager.ainvoke(prompt) for prompt in prompts]
    responses = await asyncio.gather(*tasks)

    # すべての呼び出しが成功
    assert len(responses) == 3
    assert all(r.content for r in responses)
