"""
LLMマネージャーのテスト
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm.manager import LLMManager


@pytest.fixture
def llm_manager():
    """LLMマネージャーのフィクスチャ"""
    return LLMManager()


@pytest.fixture
def mock_gemini_api():
    """GeminiのAPIモックのフィクスチャ"""
    with patch("google.generativeai.GenerativeModel") as mock:
        instance = MagicMock()
        instance.generate_content_async = AsyncMock(return_value=MagicMock(text="test response"))
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_openai_api():
    """OpenAIのAPIモックのフィクスチャ"""
    with patch("openai.AsyncOpenAI") as mock:
        instance = MagicMock()
        chat = MagicMock()
        completions = MagicMock()
        completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="test response"))],
            usage=MagicMock(prompt_tokens=10, completion_tokens=20)
        ))
        chat.completions = completions
        instance.chat = chat
        mock.return_value = instance
        yield mock


def test_load_model_gemini(llm_manager, mock_gemini_api):
    """Geminiモデルのロードテスト"""
    model = llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    assert model is not None
    assert model.model == "gemini-2.0-flash-exp"
    assert model.api_key == "test_key"


def test_load_model_gpt4(llm_manager, mock_openai_api):
    """GPT-4モデルのロードテスト"""
    model = llm_manager.load_model(
        model_name="gpt-4o",
        api_key="test_key"
    )
    assert model is not None
    assert model.model == "gpt-4o"
    assert model.api_key == "test_key"


def test_load_invalid_model(llm_manager):
    """無効なモデルのロードテスト"""
    with pytest.raises(ValueError):
        llm_manager.load_model(
            model_name="invalid-model",
            api_key="test_key"
        )


def test_get_model(llm_manager, mock_gemini_api):
    """モデルの取得テスト"""
    # モデルをロード
    model = llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    
    # モデルを取得
    retrieved_model = llm_manager.get_model("gemini-2.0-flash-exp")
    assert retrieved_model is model
    
    # 存在しないモデルを取得
    assert llm_manager.get_model("invalid-model") is None


@pytest.mark.asyncio
async def test_generate_selector(llm_manager, mock_gemini_api):
    """セレクタ生成テスト"""
    # モデルをロード
    llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    
    # セレクタを生成
    result = await llm_manager.generate_selector(
        model_name="gemini-2.0-flash-exp",
        html_content="<html><body><h1>Test</h1></body></html>"
    )
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_generate_content(llm_manager, mock_gemini_api):
    """コンテンツ生成テスト"""
    # モデルをロード
    llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    
    # コンテンツを生成
    result = await llm_manager.generate_content(
        model_name="gemini-2.0-flash-exp",
        html_content="<html><body><h1>Test</h1></body></html>"
    )
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_analyze_error(llm_manager, mock_gemini_api):
    """エラー分析テスト"""
    # モデルをロード
    llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    
    # エラーを分析
    result = await llm_manager.analyze_error(
        model_name="gemini-2.0-flash-exp",
        error_content="Test error message"
    )
    assert isinstance(result, dict)


def test_metrics(llm_manager, mock_gemini_api):
    """メトリクスのテスト"""
    # モデルをロード
    model = llm_manager.load_model(
        model_name="gemini-2.0-flash-exp",
        api_key="test_key"
    )
    
    # メトリクスを更新
    model.update_metrics(10, 20, 0.5)
    
    # メトリクスを取得
    metrics = llm_manager.get_metrics("gemini-2.0-flash-exp")
    assert metrics is not None
    assert metrics["total_tokens"] == 30
    assert metrics["prompt_tokens"] == 10
    assert metrics["completion_tokens"] == 20
    assert metrics["total_cost"] == 0.5
    
    # メトリクスをリセット
    llm_manager.reset_metrics("gemini-2.0-flash-exp")
    metrics = llm_manager.get_metrics("gemini-2.0-flash-exp")
    assert metrics["total_tokens"] == 0
    assert metrics["total_cost"] == 0.0 