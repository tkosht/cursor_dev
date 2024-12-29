"""
LLMの統合テスト
"""
import os
from typing import Dict

import pytest
from dotenv import load_dotenv

from app.llm.manager import LLMManager

# .envファイルから環境変数を読み込み
load_dotenv()

# APIキーを取得
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY_GEMINI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# テスト用のHTMLコンテンツ
TEST_HTML = """
<html>
<head>
    <title>テストページ</title>
</head>
<body>
    <h1 class="article-title">テスト記事のタイトル</h1>
    <div class="article-content">
        <p>これはテスト記事の本文です。</p>
        <p>複数の段落があります。</p>
    </div>
    <span class="publish-date">2024-01-01</span>
</body>
</html>
"""

# テスト用のエラーメッセージ
TEST_ERROR = """
Error: HTTPError
Status Code: 404
Message: Page not found
URL: https://example.com/test
Timestamp: 2024-01-01 12:00:00
"""


@pytest.fixture
def llm_manager():
    """LLMマネージャーのフィクスチャ"""
    manager = LLMManager()

    # Geminiモデルをロード
    if GEMINI_API_KEY:
        manager.load_model(model_name="gemini-2.0-flash-exp", api_key=GEMINI_API_KEY)

    # GPT-4モデルをロード
    if OPENAI_API_KEY:
        manager.load_model(model_name="gpt-4o", api_key=OPENAI_API_KEY)

    return manager


def validate_selector_result(result: Dict) -> bool:
    """
    セレクタ生成結果を検証

    Args:
        result (Dict): 検証する結果

    Returns:
        bool: 検証結果
    """
    required_keys = {"title", "content", "date"}
    if not all(key in result for key in required_keys):
        return False

    # 各セレクタが文字列であることを確認
    return all(isinstance(result[key], str) for key in required_keys)


def validate_content_result(result: Dict) -> bool:
    """
    コンテンツ抽出結果を検証

    Args:
        result (Dict): 検証する結果

    Returns:
        bool: 検証結果
    """
    required_keys = {"title", "content", "date"}
    if not all(key in result for key in required_keys):
        return False

    # 各フィールドが文字列であることを確認
    return all(isinstance(result[key], str) for key in required_keys)


def validate_error_result(result: Dict) -> bool:
    """
    エラー分析結果を検証

    Args:
        result (Dict): 検証する結果

    Returns:
        bool: 検証結果
    """
    required_keys = {"cause", "solution", "retry"}
    if not all(key in result for key in required_keys):
        return False

    # 各フィールドの型を確認
    return (
        isinstance(result["cause"], str)
        and isinstance(result["solution"], str)
        and isinstance(result["retry"], bool)
    )


@pytest.mark.skipif(not GEMINI_API_KEY, reason="Gemini API key not found")
@pytest.mark.asyncio
async def test_gemini_selector(llm_manager):
    """Geminiモデルのセレクタ生成テスト"""
    result = await llm_manager.generate_selector(
        model_name="gemini-2.0-flash-exp", html_content=TEST_HTML
    )
    assert validate_selector_result(result)


@pytest.mark.skipif(not GEMINI_API_KEY, reason="Gemini API key not found")
@pytest.mark.asyncio
async def test_gemini_content(llm_manager):
    """Geminiモデルのコンテンツ抽出テスト"""
    result = await llm_manager.generate_content(
        model_name="gemini-2.0-flash-exp", html_content=TEST_HTML
    )
    assert validate_content_result(result)


@pytest.mark.skipif(not GEMINI_API_KEY, reason="Gemini API key not found")
@pytest.mark.asyncio
async def test_gemini_error(llm_manager):
    """Geminiモデルのエラー分析テスト"""
    result = await llm_manager.analyze_error(
        model_name="gemini-2.0-flash-exp", error_content=TEST_ERROR
    )
    assert validate_error_result(result)


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not found")
@pytest.mark.asyncio
async def test_gpt4_selector(llm_manager):
    """GPT-4モデルのセレクタ生成テスト"""
    result = await llm_manager.generate_selector(
        model_name="gpt-4o", html_content=TEST_HTML
    )
    assert validate_selector_result(result)


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not found")
@pytest.mark.asyncio
async def test_gpt4_content(llm_manager):
    """GPT-4モデルのコンテンツ抽出テスト"""
    result = await llm_manager.generate_content(
        model_name="gpt-4o", html_content=TEST_HTML
    )
    assert validate_content_result(result)


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OpenAI API key not found")
@pytest.mark.asyncio
async def test_gpt4_error(llm_manager):
    """GPT-4モデルのエラー分析テスト"""
    result = await llm_manager.analyze_error(
        model_name="gpt-4o", error_content=TEST_ERROR
    )
    assert validate_error_result(result)
