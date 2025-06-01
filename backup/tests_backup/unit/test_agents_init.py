"""
agents/__init__.py の単体テスト
"""

import os
from unittest.mock import patch

from app.a2a_prototype.agents import GeminiA2AAgent, create_gemini_agent


class TestCreateGeminiAgent:
    """create_gemini_agent 関数のテスト"""

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
            "GEMINI_MODEL": "gemini-2.5-pro-preview-05-06",
        },
    )
    def test_create_with_default_parameters(self):
        """デフォルトパラメータでエージェント作成"""
        # When: デフォルト設定でエージェントを作成
        agent = create_gemini_agent()

        # Then: 適切な設定でエージェントが作成される
        assert isinstance(agent, GeminiA2AAgent)
        assert agent.config.name == "gemini-chat-agent"
        assert agent.config.port == 8004
        assert agent.config.url == "http://localhost:8004"
        assert "Advanced conversational AI agent" in agent.config.description

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
            "GEMINI_MODEL": "gemini-2.5-pro-preview-05-06",
        },
    )
    def test_create_with_custom_port(self):
        """カスタムポートでエージェント作成"""
        # When: カスタムポートでエージェントを作成
        agent = create_gemini_agent(port=9000)

        # Then: 指定されたポートが設定される
        assert agent.config.port == 9000
        assert agent.config.url == "http://localhost:9000"

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
            "GEMINI_MODEL": "gemini-2.5-pro-preview-05-06",
        },
    )
    def test_create_with_custom_name_and_description(self):
        """カスタム名前と説明でエージェント作成"""
        # When: カスタム設定でエージェントを作成
        agent = create_gemini_agent(
            name="custom-agent", description="Custom test agent"
        )

        # Then: 指定された設定が適用される
        assert agent.config.name == "custom-agent"
        assert agent.config.description == "Custom test agent"

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
            "GEMINI_MODEL": "gemini-2.5-pro-preview-05-06",
        },
    )
    def test_create_with_custom_gemini_settings(self):
        """カスタムGemini設定でエージェント作成"""
        # When: カスタムGemini設定でエージェントを作成
        agent = create_gemini_agent(
            temperature=0.9, max_tokens=500, model="gemini-1.5-pro"
        )

        # Then: Gemini設定が上書きされる
        assert agent.gemini_config.temperature == 0.9
        assert agent.gemini_config.max_tokens == 500
        assert agent.gemini_config.model == "gemini-1.5-pro"

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
        },
    )
    def test_create_with_all_custom_parameters(self):
        """全パラメータカスタムでエージェント作成"""
        # When: 全パラメータをカスタマイズしてエージェントを作成
        agent = create_gemini_agent(
            port=8888,
            name="full-custom-agent",
            description="Fully customized agent",
            version="2.0.0",
            temperature=0.3,
            max_tokens=1500,
            model="gemini-2.5-pro-preview-05-06",
        )

        # Then: 全ての設定が適用される
        assert agent.config.name == "full-custom-agent"
        assert agent.config.description == "Fully customized agent"
        assert agent.config.port == 8888
        assert agent.config.version == "2.0.0"
        assert agent.gemini_config.temperature == 0.3
        assert agent.gemini_config.max_tokens == 1500
        assert agent.gemini_config.model == "gemini-2.5-pro-preview-05-06"
