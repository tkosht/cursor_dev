"""
テスト用フィクスチャ定義
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Note: テスト実行時にはインポートパスを調整
# from app.a2a_prototype.utils.gemini_config import GeminiConfig
# from app.a2a_prototype.utils.config import AgentConfig
# from app.a2a_prototype.utils.gemini_client import GeminiClient


@pytest.fixture
def test_gemini_config_data():
    """テスト用Gemini設定データ"""
    return {
        "api_key": "test-api-key-12345678",
        "model": "gemini-2.5-pro",
        "temperature": 0.5,
        "max_tokens": 500,
    }


@pytest.fixture
def test_agent_config_data():
    """テスト用エージェント設定データ"""
    return {
        "name": "test-gemini-agent",
        "description": "Test Gemini agent",
        "url": "http://localhost:8999",
        "port": 8999,
    }


@pytest.fixture
def mock_gemini_client():
    """モックされたGeminiClient"""
    client = AsyncMock()
    client.generate_response.return_value = "Test response from Gemini"
    client.generate_response_with_timeout.return_value = (
        "Test response with timeout"
    )
    client.health_check.return_value = True
    client.get_client_info.return_value = {
        "model": "gemini-2.5-pro",
        "temperature": 0.7,
        "max_tokens": 1000,
        "initialized": True,
        "api_key_masked": "test-api********",
    }
    return client


@pytest.fixture
def mock_genai():
    """モックされたgoogle.generativeai"""
    with (
        patch("google.generativeai.configure") as mock_configure,
        patch("google.generativeai.GenerativeModel") as mock_model,
    ):

        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini response"

        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance

        yield {
            "configure": mock_configure,
            "model_class": mock_model,
            "model_instance": mock_model_instance,
            "response": mock_response,
        }


@pytest.fixture
def mock_environment_variables():
    """テスト用環境変数モック"""
    env_vars = {
        "GEMINI_API_KEY": "test-api-key-12345678",
        "GEMINI_MODEL": "gemini-2.5-pro",
        "GEMINI_TEMPERATURE": "0.7",
        "GEMINI_MAX_TOKENS": "1000",
    }

    with patch.dict("os.environ", env_vars):
        yield env_vars
