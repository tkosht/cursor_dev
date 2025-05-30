"""
Gemini A2A Agent E2E Tests

実際のGemini APIを使用したエンドツーエンドテスト
"""

import os

import pytest
from dotenv import load_dotenv

from app.a2a_prototype.agents.gemini_agent import GeminiA2AAgent
from app.a2a_prototype.utils.config import AgentConfig
from app.a2a_prototype.utils.gemini_config import GeminiConfig

# .envファイルを読み込み
load_dotenv()

# APIキーが設定されているかチェック
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
pytestmark = pytest.mark.skipif(
    not GEMINI_API_KEY,
    reason="GEMINI_API_KEY environment variable is required for E2E tests",
)


class TestGeminiAgentE2E:
    """Gemini A2A Agent エンドツーエンドテスト"""

    @pytest.fixture
    def real_configs(self):
        """実際のAPIキーを使用した設定"""
        agent_config = AgentConfig(
            name="test-gemini-agent-e2e",
            description="E2E test agent with real API",
            url="http://localhost:8005",
            port=8005,
        )

        gemini_config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model="gemini-2.5-pro-preview-05-06",
            temperature=0.5,
            max_tokens=300,  # E2Eテストでは短めに設定
        )

        return agent_config, gemini_config

    @pytest.mark.asyncio
    async def test_real_gemini_api_connection(self, real_configs):
        """実際のGemini APIとの接続テスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: ヘルスチェックを実行
        health = await agent.gemini_client.health_check()

        # Then: APIが正常に応答する
        assert health is True, "Gemini API health check should pass"

    @pytest.mark.asyncio
    async def test_real_simple_conversation(self, real_configs):
        """実際のAPIを使用した基本対話テスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 簡単な挨拶メッセージを送信
        response = await agent.process_user_input("こんにちは")

        # Then: 適切な応答が返される
        assert response is not None
        assert len(response) > 0
        
        # APIエラーの場合はスキップ（実際のAPIの制限を考慮）
        if "申し訳ございません" in response:
            pytest.skip(
                "Gemini API returned error - likely rate limit or safety filter"
            )
            
        print(f"Response: {response}")

    @pytest.mark.asyncio
    async def test_real_conversation_context(self, real_configs):
        """実際のAPIを使用した会話コンテキストテスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 連続した会話を実行（より安全なプロンプト）
        response1 = await agent.process_user_input(
            "Hello, my name is TestUser"
        )
        response2 = await agent.process_user_input("What is my name?")

        # Then: 両方の応答が正常で、文脈が維持される
        assert response1 is not None and len(response1) > 0
        assert response2 is not None and len(response2) > 0

        # APIエラーの場合はスキップ（実際のAPIの制限を考慮）
        if (
            "申し訳ございません" in response1
            or "申し訳ございません" in response2
        ):
            pytest.skip(
                "Gemini API returned error - likely rate limit or safety filter"
            )

        # 正常な応答の場合のみコンテキストチェック

        # 会話履歴が記録されている
        assert len(agent.conversation_context) == 4  # 2往復分
        print(f"Context: {agent.conversation_context}")

    @pytest.mark.asyncio
    async def test_help_command_workflow(self, real_configs):
        """ヘルプコマンドワークフローテスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: ヘルプコマンドを実行
        response = await agent.process_user_input("help")

        # Then: ヘルプメッセージが返される
        assert "Gemini 2.5 Pro搭載エージェント" in response
        assert "使い方:" in response
        assert "status" in response
        assert "clear" in response
        assert "何でもお気軽にお聞かせください" in response

    @pytest.mark.asyncio
    async def test_status_command_workflow(self, real_configs):
        """ステータスコマンドワークフローテスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: ステータスコマンドを実行
        response = await agent.process_user_input("status")

        # Then: ステータス情報が返される
        assert "test-gemini-agent-e2e" in response
        assert "gemini-2.5-pro-preview-05-06" in response
        assert "✅ OK" in response or "❌ ERROR" in response
        assert "Context: 0 messages" in response  # 初期状態

    @pytest.mark.asyncio
    async def test_clear_command_workflow(self, real_configs):
        """クリアコマンドワークフローテスト"""
        # Given: 会話履歴があるエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # 事前に会話を実行して履歴を作成
        await agent.process_user_input("テスト会話です")

        # When: クリアコマンドを実行
        response = await agent.process_user_input("clear")

        # Then: 履歴がクリアされる
        assert "会話履歴をクリアしました" in response
        assert len(agent.conversation_context) == 0

    @pytest.mark.asyncio
    async def test_agent_skills_functionality(self, real_configs):
        """エージェントスキル機能テスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: スキル一覧を取得
        skills = agent.get_skills()

        # Then: 期待されるスキルが定義されている
        assert len(skills) == 3
        skill_ids = [skill.id for skill in skills]
        assert "chat" in skill_ids
        assert "qa" in skill_ids
        assert "help" in skill_ids

        # 各スキルの必須フィールドが設定されている
        for skill in skills:
            assert skill.id is not None
            assert skill.name is not None
            assert skill.description is not None
            assert skill.tags is not None and len(skill.tags) > 0

    @pytest.mark.asyncio
    async def test_error_handling_invalid_input(self, real_configs):
        """エラーハンドリングテスト（無効入力）"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 空の入力を送信
        response = await agent.process_user_input("")

        # Then: 適切なエラーメッセージが返される
        assert "入力エラー" in response
        assert "入力が空です" in response

    @pytest.mark.asyncio
    async def test_error_handling_long_input(self, real_configs):
        """エラーハンドリングテスト（長すぎる入力）"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 長すぎる入力を送信
        long_input = "a" * (agent.MAX_INPUT_LENGTH + 1)
        response = await agent.process_user_input(long_input)

        # Then: 適切なエラーメッセージが返される
        assert "入力エラー" in response
        assert "入力が長すぎます" in response

    @pytest.mark.asyncio
    async def test_agent_stats_after_conversation(self, real_configs):
        """会話後のエージェント統計情報テスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: 複数回会話を実行
        await agent.process_user_input("最初のメッセージ")
        await agent.process_user_input("二番目のメッセージ")
        stats = agent.get_agent_stats()

        # Then: 正確な統計情報が記録される
        assert stats["conversation_messages"] == 4  # 2往復分
        assert stats["max_context_messages"] == 20
        assert stats["gemini_model"] == "gemini-2.5-pro-preview-05-06"
        assert stats["gemini_temperature"] == 0.5
        assert stats["skills_count"] == 3

    @pytest.mark.asyncio
    async def test_response_time_performance(self, real_configs):
        """レスポンス時間パフォーマンステスト"""
        # Given: 実際のAPIキーを使用したエージェント
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # When: シンプルな質問を送信（時間測定）
        import time

        start_time = time.time()
        response = await agent.process_user_input("Hello")
        end_time = time.time()

        # Then: 合理的な時間内で応答する（10秒以内）
        response_time = end_time - start_time
        assert (
            response_time < 10.0
        ), f"Response time {response_time:.2f}s should be < 10s"
        assert response is not None and len(response) > 0
        print(f"Response time: {response_time:.2f} seconds")


@pytest.mark.asyncio
@pytest.mark.slow
async def test_gemini_agent_full_workflow():
    """完全ワークフローテスト（統合シナリオ）"""
    # .envファイルを再読み込み（念のため）
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        pytest.skip("GEMINI_API_KEY required for full workflow test")

    # Given: 実際のAPIキーを使用したエージェント
    agent_config = AgentConfig(
        name="full-workflow-test-agent",
        description="Complete workflow test agent",
        url="http://localhost:8006",
        port=8006,
    )

    gemini_config = GeminiConfig(
        api_key=api_key,
        model="gemini-2.5-pro-preview-05-06",
        temperature=0.7,
        max_tokens=500,
    )

    agent = GeminiA2AAgent(agent_config, gemini_config)

    # When & Then: 完全なユーザーシナリオを実行
    # 1. 初期状態確認
    assert len(agent.conversation_context) == 0

    # 2. ヘルプコマンド
    help_response = await agent.process_user_input("help")
    assert "Gemini 2.5 Pro搭載エージェント" in help_response

    # 3. 状態確認
    status_response = await agent.process_user_input("status")
    assert "full-workflow-test-agent" in status_response

    # 4. 実際の対話
    chat_response = await agent.process_user_input(
        "AIについて簡単に教えてください"
    )
    assert len(chat_response) > 0
    
    # APIエラーの場合はスキップ（実際のAPIの制限を考慮）
    if "申し訳ございません" in chat_response:
        pytest.skip(
            "Gemini API returned error - likely rate limit or safety filter"
        )

    # 5. 文脈を持った追加質問
    followup_response = await agent.process_user_input(
        "もう少し詳しく教えてください"
    )
    assert len(followup_response) > 0

    # 6. 会話履歴確認
    assert len(agent.conversation_context) == 4  # 2往復分

    # 7. 履歴クリア
    clear_response = await agent.process_user_input("clear")
    assert "会話履歴をクリアしました" in clear_response
    assert len(agent.conversation_context) == 0

    # 8. 最終統計確認
    stats = agent.get_agent_stats()
    assert stats["skills_count"] == 3
    assert stats["gemini_model"] == "gemini-2.5-pro-preview-05-06"

    print("✅ Full workflow test completed successfully")
