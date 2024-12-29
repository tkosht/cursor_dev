"""
GeminiLLMクラスのテスト
"""
import asyncio
from unittest.mock import Mock, patch

import pytest

from app.llm.gemini import GeminiLLM


@pytest.fixture
def gemini_config():
    """Gemini LLMの設定"""
    return {
        "api_key": "test_api_key",
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.1
    }


@pytest.fixture
def mock_client():
    """モックされたGeminiクライアント"""
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model:
        mock_instance = Mock()
        mock_model.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def gemini_llm(gemini_config, mock_client):
    """GeminiLLMインスタンス"""
    llm = GeminiLLM(**gemini_config)
    llm.client = mock_client
    return llm


def test_init_client_success(gemini_config):
    """クライアント初期化の成功テスト"""
    llm = GeminiLLM(**gemini_config)
    assert llm.client is not None


def test_init_client_no_api_key():
    """API keyなしでの初期化テスト"""
    with pytest.raises(ValueError) as exc_info:
        GeminiLLM(api_key=None)
    assert "APIキーが設定されていません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_success(gemini_llm):
    """テキスト生成の成功テスト"""
    mock_response = Mock()
    mock_response.text = "生成されたテキスト"
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future
    
    result = await gemini_llm.generate_text("テストプロンプト")
    
    assert result == "生成されたテキスト"
    gemini_llm.client.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_success(gemini_llm):
    """コンテンツ分析の成功テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future
    
    result = await gemini_llm.analyze_content(
        "テストコンテンツ",
        "test_task"
    )
    
    assert result == {"key": "value"}
    gemini_llm.client.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_metrics_update(gemini_llm):
    """メトリクス更新のテスト"""
    mock_response = Mock()
    mock_response.text = "テストレスポンス"
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future
    
    await gemini_llm.generate_text("テストプロンプト")
    
    # プロンプトとレスポンスの文字数でメトリクスが更新されていることを確認
    assert gemini_llm.metrics.prompt_tokens > 0
    assert gemini_llm.metrics.completion_tokens > 0
    assert gemini_llm.metrics.total_cost == 0.0  # 現在は無料


@pytest.mark.asyncio
async def test_json_extraction(gemini_llm):
    """JSONコンテンツ抽出のテスト"""
    test_cases = [
        # 正常なJSONケース
        {
            "input": '{"key": "value"}',
            "expected": {"key": "value"}
        },
        # JSONが文章の中に埋め込まれているケース
        {
            "input": "分析結果は以下の通りです：\n{\"key\": \"value\"}\n以上です。",
            "expected": {"key": "value"}
        },
        # 不正なJSONケース
        {
            "input": "これはJSONではありません",
            "expected": {"text": "これはJSONではありません"}
        }
    ]
    
    for case in test_cases:
        result = gemini_llm._extract_content(case["input"])
        assert result == case["expected"]


@pytest.mark.asyncio
async def test_retry_on_error(gemini_llm):
    """エラー時のリトライ機能のテスト"""
    # 2回失敗して3回目で成功するモックを作成
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        mock_response
    ]
    
    result = await gemini_llm._analyze_content_impl("test", "test_task")
    
    # 3回呼び出されたことを確認
    assert gemini_llm.client.generate_content_async.call_count == 3
    # 最終的に成功したレスポンスが返されることを確認
    assert isinstance(result, dict) 