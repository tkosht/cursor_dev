"""
Gemini A2A Agent 統合テスト

各コンポーネントの統合動作を確認
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.a2a_prototype.agents.gemini_agent import GeminiA2AAgent
from app.a2a_prototype.utils.config import AgentConfig
from app.a2a_prototype.utils.gemini_config import GeminiConfig


class TestGeminiA2AIntegration:
    """Gemini A2A Agent統合テスト"""

    @pytest.fixture
    def test_configs(self):
        """テスト用設定"""
        agent_config = AgentConfig(
            name="test-gemini-agent",
            description="Test Gemini agent",
            url="http://localhost:8999",
            port=8999,
        )

        gemini_config = GeminiConfig(
            api_key="test-api-key-12345678",
            model="gemini-2.5-pro",
            temperature=0.5,
            max_tokens=500,
        )

        return agent_config, gemini_config

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    def test_agent_initialization(self, mock_genai, test_configs):
        """エージェントの初期化テスト"""
        # Given: モックされたGemini API
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # When: Geminiエージェントを作成
        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # Then: 正常に初期化される
        assert agent.config.name == "test-gemini-agent"
        assert agent.gemini_config.model == "gemini-2.5-pro"
        assert len(agent.get_skills()) == 3
        assert agent.conversation_context == []

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_help_command(self, mock_genai, test_configs):
        """ヘルプコマンドテスト"""
        # Given: モックされたGemini API
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: ヘルプコマンドを実行
        response = await agent.process_user_input("help")

        # Then: ヘルプメッセージが返される
        assert "Gemini 2.5 Pro搭載エージェント" in response
        assert "使い方:" in response
        assert "status" in response
        assert "clear" in response

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_clear_command(self, mock_genai, test_configs):
        """クリアコマンドテスト"""
        # Given: 会話履歴があるエージェント
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # 履歴を追加
        agent.conversation_context = ["User: test", "Assistant: response"]

        # When: クリアコマンドを実行
        response = await agent.process_user_input("clear")

        # Then: 履歴がクリアされる
        assert agent.conversation_context == []
        assert "会話履歴をクリアしました" in response

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_status_command_with_mock_health_check(
        self, mock_genai, test_configs
    ):
        """ステータスコマンドテスト（ヘルスチェック含む）"""
        # Given: モックされたGemini API
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # ヘルスチェックをモック
        agent.gemini_client.health_check = AsyncMock(return_value=True)

        # When: ステータスコマンドを実行
        response = await agent.process_user_input("status")

        # Then: ステータス情報が返される
        assert "test-gemini-agent" in response
        assert "gemini-2.5-pro" in response
        assert "✅ OK" in response
        assert "test-api********" in response

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_normal_conversation_with_mock_api(self, mock_genai, test_configs):
        """通常対話テスト（モックAPI）"""
        # Given: モックされたGemini API（成功レスポンス）
        mock_response = MagicMock()
        mock_response.text = "こんにちは！何かお手伝いできることはありますか？"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 通常のメッセージを送信
        response = await agent.process_user_input("こんにちは")

        # Then: Geminiからの応答が返される
        assert response == "こんにちは！何かお手伝いできることはありますか？"

        # 会話履歴が更新される
        assert len(agent.conversation_context) == 2
        assert "User: こんにちは" in agent.conversation_context
        assert "Assistant: こんにちは！何かお手伝いできることはありますか？" in agent.conversation_context

    def test_get_skills(self, test_configs):
        """スキル一覧取得テスト"""
        # Given: モックされたGemini API
        with patch("app.a2a_prototype.utils.gemini_client.genai"):
            agent_config, gemini_config = test_configs
            agent = GeminiA2AAgent(agent_config, gemini_config)

            # When: スキル一覧を取得
            skills = agent.get_skills()

            # Then: 期待されるスキルが返される
            assert len(skills) == 3
            skill_ids = [skill.id for skill in skills]
            assert "chat" in skill_ids
            assert "qa" in skill_ids
            assert "help" in skill_ids

    def test_get_agent_stats(self, test_configs):
        """エージェント統計情報取得テスト"""
        # Given: 会話履歴があるエージェント
        with patch("app.a2a_prototype.utils.gemini_client.genai"):
            agent_config, gemini_config = test_configs
            agent = GeminiA2AAgent(agent_config, gemini_config)

            # 履歴を追加
            agent.conversation_context = ["User: test1", "Assistant: response1"]

            # When: 統計情報を取得
            stats = agent.get_agent_stats()

            # Then: 期待される統計情報が返される
            assert stats["conversation_messages"] == 2
            assert stats["max_context_messages"] == 20
            assert stats["gemini_model"] == "gemini-2.5-pro"
            assert stats["gemini_temperature"] == 0.5
            assert stats["skills_count"] == 3

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_input_validation_empty(self, mock_genai, test_configs):
        """入力バリデーションテスト（空入力）"""
        # Given: モックされたGemini API
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 空の入力を送信
        response = await agent.process_user_input("")

        # Then: エラーメッセージが返される
        assert "入力エラー" in response
        assert "入力が空です" in response

    @patch("app.a2a_prototype.utils.gemini_client.genai")
    async def test_input_validation_too_long(self, mock_genai, test_configs):
        """入力バリデーションテスト（長すぎる入力）"""
        # Given: モックされたGemini API
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        agent_config, gemini_config = test_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 長すぎる入力を送信
        long_input = "a" * (agent.MAX_INPUT_LENGTH + 1)
        response = await agent.process_user_input(long_input)

        # Then: エラーメッセージが返される
        assert "入力エラー" in response
        assert "入力が長すぎます" in response 