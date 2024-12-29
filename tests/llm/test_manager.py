"""
LLMマネージャーのテスト
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm.manager import LLMManager


@pytest.fixture
def llm_config():
    """LLMの設定"""
    return {
        "model_name": "gemini-2.0-flash-exp",
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 30.0
    }


@pytest.fixture
def mock_gemini_api():
    """GeminiのAPIモックのフィクスチャ"""
    with patch("google.generativeai.GenerativeModel") as mock:
        instance = MagicMock()
        instance.generate_content_async = AsyncMock(return_value=MagicMock(text="test response"))
        mock.return_value = instance
        yield mock


@pytest.fixture
def llm_manager(llm_config):
    """LLMマネージャーのインスタンス"""
    manager = LLMManager()
    manager.load_model("gemini-2.0-flash-exp", "test_api_key")
    return manager


@pytest.mark.asyncio
async def test_evaluate_url_relevance(llm_manager):
    """URL評価のテスト"""
    # テスト用のURL情報
    url = "https://example.com/company/about"
    path_components = ["company", "about"]
    query_params = {}

    # モックレスポンスの設定
    mock_response = {
        "relevance_score": 0.95,
        "category": "company_profile",
        "reason": "企業情報を含むパス構造",
        "confidence": 0.9
    }
    llm_manager.llm.analyze_content = AsyncMock(return_value=mock_response)

    # 評価を実行
    result = await llm_manager.evaluate_url_relevance(
        url=url,
        path_components=path_components,
        query_params=query_params
    )

    # 結果を検証
    assert result is not None
    assert result["relevance_score"] == 0.95
    assert result["category"] == "company_profile"
    assert result["reason"] == "企業情報を含むパス構造"
    assert result["confidence"] == 0.9

    # LLMが正しく呼び出されたことを確認
    llm_manager.llm.analyze_content.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_url_relevance_error(llm_manager):
    """URL評価のエラーテスト"""
    # LLMの呼び出しでエラーを発生させる
    llm_manager.llm.analyze_content = AsyncMock(side_effect=Exception("API error"))

    # 評価を実行
    result = await llm_manager.evaluate_url_relevance(
        url="https://example.com",
        path_components=["error"],
        query_params={}
    )

    # エラー時はNoneが返されることを確認
    assert result is None


@pytest.mark.asyncio
async def test_evaluate_url_relevance_invalid_result(llm_manager):
    """不正な結果のテスト"""
    # 不正なレスポンスを返すようにモックを設定
    llm_manager.llm.analyze_content = AsyncMock(return_value={
        "relevance_score": 2.0,  # 不正な値
        "category": "invalid",  # 不正なカテゴリ
        "reason": "test",
        "confidence": 0.5
    })

    # 評価を実行
    result = await llm_manager.evaluate_url_relevance(
        url="https://example.com",
        path_components=["test"],
        query_params={}
    )

    # 不正な結果の場合はNoneが返されることを確認
    assert result is None 