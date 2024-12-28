"""
GeminiLLMクラスのテスト
"""
import asyncio
from unittest.mock import Mock, patch

import pytest

from app.llm.base import LLMConnectionError, LLMResponseError
from app.llm.gemini import GeminiLLM
from app.llm.prompts import PromptManager


@pytest.fixture
def gemini_config():
    """Gemini LLMの設定"""
    return {
        "name": "gemini-2.0-flash-exp",
        "api_key": "test_api_key",
        "provider": "google"
    }


@pytest.fixture
def mock_client():
    """モックされたGeminiクライアント"""
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model:
        yield mock_model


@pytest.fixture
def gemini_llm(gemini_config, mock_client):
    """GeminiLLMインスタンス"""
    return GeminiLLM(gemini_config)


def test_init_client_success(gemini_config, mock_client):
    """クライアント初期化の成功テスト"""
    llm = GeminiLLM(gemini_config)
    assert llm.client is not None


def test_init_client_no_api_key():
    """API keyなしでの初期化テスト"""
    config = {"name": "gemini-2.0-flash-exp"}
    with pytest.raises(LLMConnectionError) as exc_info:
        GeminiLLM(config)
    assert "API key is not provided" in str(exc_info.value)


def test_parse_response_success(gemini_llm):
    """レスポンスパースの成功テスト"""
    response = Mock()
    response.text = "テストレスポンス"
    
    result = gemini_llm._parse_response(response)
    assert result == "テストレスポンス"


def test_parse_response_empty(gemini_llm):
    """空レスポンスのパーステスト"""
    response = Mock()
    response.text = ""
    
    with pytest.raises(LLMResponseError) as exc_info:
        gemini_llm._parse_response(response)
    assert "Empty response" in str(exc_info.value)


def test_process_content_line(gemini_llm):
    """コンテンツ行処理のテスト"""
    # キー行のテスト
    key, value, result = gemini_llm._process_content_line(
        "テストキー:",
        None,
        []
    )
    assert key == "テストキー"
    assert value == []
    assert result is None
    
    # 値行のテスト
    key, value, result = gemini_llm._process_content_line(
        "テスト値",
        "テストキー",
        []
    )
    assert key == "テストキー"
    assert value == ["テスト値"]
    assert result is None
    
    # 新しいキーへの移行テスト
    key, value, result = gemini_llm._process_content_line(
        "新しいキー:",
        "前のキー",
        ["値1", "値2"]
    )
    assert key == "新しいキー"
    assert value == []
    assert result == ("前のキー", "値1\n値2")


def test_build_content_dict(gemini_llm):
    """コンテンツ辞書構築のテスト"""
    content = """
    キー1:
    値1-1
    値1-2
    
    キー2:
    値2
    
    キー3:
    値3
    """
    
    result = gemini_llm._build_content_dict(content)
    assert result == {
        "キー1": "値1-1\n値1-2",
        "キー2": "値2",
        "キー3": "値3"
    }


def test_extract_content_success(gemini_llm):
    """コンテンツ抽出の成功テスト"""
    response = Mock()
    response.text = """
    キー1:
    値1
    
    キー2:
    値2
    """
    
    result = gemini_llm._extract_content(response)
    assert result == {
        "キー1": "値1",
        "キー2": "値2"
    }


def test_extract_content_empty(gemini_llm):
    """空コンテンツの抽出テスト"""
    response = Mock()
    response.text = ""
    
    with pytest.raises(LLMResponseError) as exc_info:
        gemini_llm._extract_content(response)
    assert "Empty content" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_success(gemini_llm):
    """テキスト生成の成功テスト"""
    mock_response = Mock()
    mock_response.text = "生成されたテキスト"
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future
    
    result = await gemini_llm.generate(
        "テストプロンプト",
        temperature=0.7,
        max_tokens=1000
    )
    
    assert result == "生成されたテキスト"
    gemini_llm.client.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_success(gemini_llm):
    """コンテンツ分析の成功テスト"""
    mock_response = Mock()
    mock_response.text = """
    分析結果:
    テスト結果です
    
    信頼度:
    高
    """
    
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future
    
    result = await gemini_llm.analyze(
        "テストコンテンツ",
        "content_extraction",
        temperature=0.1
    )
    
    assert result == {
        "分析結果": "テスト結果です",
        "信頼度": "高"
    }
    gemini_llm.client.generate_content_async.assert_called_once()


def test_prompt_manager():
    """プロンプトマネージャーのテスト"""
    # セレクター生成タスク
    selector_prompt = PromptManager.format_prompt(
        "selector_generation",
        "<div>テスト</div>"
    )
    assert "HTMLから必要な情報を抽出するための最適なCSSセレクター" in selector_prompt
    
    # コンテンツ抽出タスク
    content_prompt = PromptManager.format_prompt(
        "content_extraction",
        "<div>テスト</div>"
    )
    assert "HTMLから情報を抽出し、構造化してください" in content_prompt
    
    # エラー分析タスク
    error_prompt = PromptManager.format_prompt(
        "error_analysis",
        "エラーメッセージ"
    )
    assert "エラー情報を分析し、対処方法を提案してください" in error_prompt
    
    # 未知のタスク
    unknown_prompt = PromptManager.format_prompt(
        "unknown_task",
        "テスト"
    )
    assert "以下の内容を分析してください" in unknown_prompt 