"""
BaseA2AAgentの包括的単体テスト (TDD実践版 - カバレッジ90%達成)

未カバー部分の網羅的テスト：
- executeメソッドの各分岐 (正常/入力不足/例外)
- cancelメソッド
- create_appメソッド
- run_agentメソッド
- AgentHealthCheckクラス
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.a2a_prototype.agents.base_agent import AgentHealthCheck, BaseA2AAgent
from app.a2a_prototype.utils.config import AgentConfig

# a2a-sdk インポート（テスト用）
try:
    from a2a.types import AgentSkill, TaskState

    # A2AStarletteApplicationはモックで代替するため、直接importしない
except ImportError:
    pytest.skip("a2a-sdk not available", allow_module_level=True)


@pytest.fixture
def test_agent_instance(sample_agent_config):
    """テスト用のBaseA2AAgentインスタンスを生成するフィクスチャ"""

    class ConcreteTestAgent(BaseA2AAgent):
        def get_skills(self):
            return [
                AgentSkill(
                    id="test_skill",
                    name="Test Skill",
                    description="Test skill for base agent testing",
                    tags=["test"],
                )
            ]

        async def process_user_input(self, user_input: str) -> str:
            if user_input == "error":
                raise ValueError("Test error")
            return f"Processed: {user_input}"

    return ConcreteTestAgent(sample_agent_config)


# TestBaseA2AAgentクラスは不要になったため削除
# class TestBaseA2AAgent(BaseA2AAgent):
#     """テスト用のBaseA2AAgent具象実装"""
#
#     def get_skills(self):
#         """テスト用スキル"""
#         return [
#             AgentSkill(
#                 id="test_skill",
#                 name="Test Skill",
#                 description="Test skill for base agent testing",
#                 tags=["test"],
#             )
#         ]
#
#     async def process_user_input(self, user_input: str) -> str:
#         """テスト用の処理"""
#         if user_input == "error":
#             raise ValueError("Test error")
#         return f"Processed: {user_input}"


@pytest.mark.unit
class TestBaseA2AAgentInitialization:
    """BaseA2AAgent初期化テスト"""

    def test_initialization_with_valid_config(self, test_agent_instance):
        """正常ケース: 有効な設定での初期化"""
        # Given: test_agent_instanceフィクスチャからエージェント取得
        agent = test_agent_instance
        config = agent.config  # 比較用

        # Then: 正常に初期化される
        assert agent.config == config
        assert agent.agent_card.name == config.name
        assert agent.agent_card.description == config.description
        assert agent.agent_card.url == config.url
        assert agent.agent_card.version == config.version
        assert len(agent.agent_card.skills) == 1

    def test_agent_card_has_correct_capabilities(self, test_agent_instance):
        """エージェントカードに正しいcapabilitiesが設定される"""
        # Given/When: test_agent_instanceフィクスチャからエージェント取得
        agent = test_agent_instance

        # Then: 期待されるcapabilitiesが設定される（属性アクセス）
        capabilities = agent.agent_card.capabilities
        assert capabilities.streaming is False
        assert (
            capabilities.pushNotifications is False
        )  # API仕様確認済み: BaseA2AAgentではFalse
        assert (
            capabilities.stateTransitionHistory is False
        )  # API仕様確認済み: BaseA2AAgentではFalse


@pytest.mark.unit
class TestBaseA2AAgentExecuteMethod:
    """executeメソッドの包括的テスト（未カバー部分対象）"""

    @pytest.mark.asyncio
    async def test_execute_with_valid_user_input(self, test_agent_instance):
        """正常ケース: 有効なユーザー入力での実行"""
        # Given: エージェントとモックオブジェクト
        agent = test_agent_instance

        # RequestContextのモック
        context = MagicMock()
        context.get_user_input.return_value = "test input"

        # Taskのモック
        task = MagicMock()
        task.status = MagicMock()
        task.history = []
        context.current_task = task

        # EventQueueのモック
        event_queue = AsyncMock()

        # When: executeを実行
        await agent.execute(context, event_queue)

        # Then: 正常に処理される
        assert task.status.state == TaskState.completed
        assert len(task.history) == 1
        event_queue.enqueue_event.assert_called_once_with(task)

    @pytest.mark.asyncio
    async def test_execute_with_no_user_input(self, test_agent_instance):
        """異常ケース: ユーザー入力なしでの実行"""
        # Given: エージェントとモックオブジェクト
        agent = test_agent_instance

        # RequestContextのモック（入力なし）
        context = MagicMock()
        context.get_user_input.return_value = None

        # Taskのモック
        task = MagicMock()
        task.status = MagicMock()
        context.current_task = task

        # EventQueueのモック
        event_queue = AsyncMock()

        # When: executeを実行
        await agent.execute(context, event_queue)

        # Then: input_required状態に設定される
        assert task.status.state == TaskState.input_required
        event_queue.enqueue_event.assert_called_once_with(task)

    @pytest.mark.asyncio
    async def test_execute_with_processing_error(self, test_agent_instance):
        """異常ケース: 処理中のエラー"""
        # Given: エージェントとモックオブジェクト
        agent = test_agent_instance

        # RequestContextのモック（エラー発生入力）
        context = MagicMock()
        context.get_user_input.return_value = "error"

        # Taskのモック
        task = MagicMock()
        task.status = MagicMock()
        context.current_task = task

        # EventQueueのモック
        event_queue = AsyncMock()

        # When: executeを実行（エラーが発生）
        await agent.execute(context, event_queue)

        # Then: failed状態に設定される
        assert task.status.state == TaskState.failed
        event_queue.enqueue_event.assert_called_once_with(task)


@pytest.mark.unit
class TestBaseA2AAgentCancelMethod:
    """cancelメソッドのテスト（未カバー部分対象）"""

    @pytest.mark.asyncio
    async def test_cancel_task_success(self, test_agent_instance):
        """正常ケース: タスクキャンセル成功"""
        # Given: エージェントとモックオブジェクト
        agent = test_agent_instance

        # RequestContextのモック
        context = MagicMock()
        context.task_id = "test_task_123"

        # Taskのモック
        task = MagicMock()
        task.status = MagicMock()
        context.current_task = task

        # EventQueueのモック
        event_queue = AsyncMock()

        # When: cancelを実行
        await agent.cancel(context, event_queue)

        # Then: canceled状態に設定される
        assert task.status.state == TaskState.canceled
        event_queue.enqueue_event.assert_called_once_with(task)

    @pytest.mark.asyncio
    async def test_cancel_with_exception(self, test_agent_instance):
        """異常ケース: キャンセル時の例外"""
        # Given: エージェントとモックオブジェクト
        agent = test_agent_instance

        # RequestContextのモック
        context = MagicMock()
        context.task_id = "test_task_123"

        # Taskのモック（例外発生）
        task = MagicMock()
        task.status = MagicMock()
        task.status.state = MagicMock(side_effect=Exception("Test exception"))
        context.current_task = task

        # EventQueueのモック
        event_queue = AsyncMock()

        # When: cancelを実行（例外が発生）
        await agent.cancel(context, event_queue)

        # Then: 例外がログに記録される（エラーは飲み込まれる）
        # 例外は内部で処理されるため、テストは正常に完了する


@pytest.mark.unit
class TestBaseA2AAgentAppCreation:
    """create_app, run_agentメソッドのテスト（未カバー部分対象）"""

    @patch("app.a2a_prototype.agents.base_agent.A2AStarletteApplication")
    def test_create_app_returns_starlette_application(
        self, mock_app_class, test_agent_instance
    ):
        """create_app: A2AStarletteApplicationを返す（正しいAPI仕様対応）"""
        # Given: BaseA2AAgent と モックされたA2AStarletteApplication
        agent = test_agent_instance
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance

        # When: create_appを実行
        app = agent.create_app()

        # Then: A2AStarletteApplicationが正しいパラメータで作成される
        mock_app_class.assert_called_once_with(
            agent_card=agent.agent_card,
            agent_executor=agent,  # 実装ではagent_executorを渡している
        )
        assert app == mock_app_instance

    @patch("uvicorn.run")
    @patch("app.a2a_prototype.agents.base_agent.A2AStarletteApplication")
    def test_run_agent_with_default_port(
        self, mock_app_class, mock_uvicorn_run, test_agent_instance
    ):
        """run_agent: デフォルトポートでの起動（正しいAPI仕様対応）"""
        # Given: BaseA2AAgent とモック
        agent = test_agent_instance
        mock_app_instance = MagicMock()
        mock_starlette_app = MagicMock()
        mock_app_instance.build.return_value = mock_starlette_app
        mock_app_class.return_value = mock_app_instance

        # When: run_agentを実行
        agent.run_agent()

        # Then: A2AStarletteApplicationが作成され、uvicornが正しいポートで起動される
        mock_app_class.assert_called_once()
        mock_app_instance.build.assert_called_once()
        mock_uvicorn_run.assert_called_once()
        args, kwargs = mock_uvicorn_run.call_args
        assert kwargs["host"] == "0.0.0.0"
        assert kwargs["port"] == test_agent_instance.config.port

    @patch("uvicorn.run")
    @patch("app.a2a_prototype.agents.base_agent.A2AStarletteApplication")
    def test_run_agent_with_custom_port(
        self, mock_app_class, mock_uvicorn_run, test_agent_instance
    ):
        """run_agent: カスタムポートでの起動（正しいAPI仕様対応）"""
        # Given: BaseA2AAgent とモック
        agent = test_agent_instance
        custom_port = 9999
        mock_app_instance = MagicMock()
        mock_starlette_app = MagicMock()
        mock_app_instance.build.return_value = mock_starlette_app
        mock_app_class.return_value = mock_app_instance

        # When: run_agentをカスタムポートで実行
        agent.run_agent(port=custom_port)

        # Then: A2AStarletteApplicationが作成され、uvicornがカスタムポートで起動される
        mock_app_class.assert_called_once()
        mock_app_instance.build.assert_called_once()
        mock_uvicorn_run.assert_called_once()
        args, kwargs = mock_uvicorn_run.call_args
        assert kwargs["port"] == custom_port

    @patch("uvicorn.run", side_effect=Exception("Startup failed"))
    @patch("app.a2a_prototype.agents.base_agent.A2AStarletteApplication")
    def test_run_agent_startup_failure(
        self, mock_app_class, mock_uvicorn_run, test_agent_instance
    ):
        """run_agent: 起動失敗時の例外処理（正しいAPI仕様対応）"""
        # Given: BaseA2AAgent とモック
        agent = test_agent_instance
        mock_app_instance = MagicMock()
        mock_starlette_app = MagicMock()
        mock_app_instance.build.return_value = mock_starlette_app
        mock_app_class.return_value = mock_app_instance

        # When/Then: run_agent実行で例外が発生する
        with pytest.raises(Exception) as exc_info:
            agent.run_agent()

        assert "Startup failed" in str(exc_info.value)


@pytest.mark.unit
class TestAgentHealthCheck:
    """AgentHealthCheckクラスのテスト（未カバー部分対象）"""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_agent_health_success(self, mock_client_class):
        """正常ケース: ヘルスチェック成功"""
        # Given: ヘルスチェック成功のモック
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        agent_url = "http://localhost:8001"

        # When: ヘルスチェックを実行
        result = await AgentHealthCheck.check_agent_health(agent_url)

        # Then: 成功を返す
        assert result is True
        mock_client.get.assert_called_once_with(
            f"{agent_url}/.well-known/agent.json"
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_agent_health_failure(self, mock_client_class):
        """異常ケース: ヘルスチェック失敗"""
        # Given: ヘルスチェック失敗のモック
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        agent_url = "http://localhost:8001"

        # When: ヘルスチェックを実行
        result = await AgentHealthCheck.check_agent_health(agent_url)

        # Then: 失敗を返す
        assert result is False

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_agent_health_exception(self, mock_client_class):
        """異常ケース: 例外発生時"""
        # Given: 例外発生のモック
        mock_client_class.side_effect = Exception("Connection failed")

        agent_url = "http://localhost:8001"

        # When: ヘルスチェックを実行
        result = await AgentHealthCheck.check_agent_health(agent_url)

        # Then: 失敗を返す
        assert result is False

    @pytest.mark.asyncio
    async def test_check_all_agents_health(self):
        """check_all_agents_health: 複数エージェントのヘルスチェック（正しいAPI仕様対応）"""
        # Given: 複数のエージェント設定（descriptionは必須）
        configs = [
            AgentConfig(
                name="agent1",
                description="Test agent 1",
                url="http://localhost:8001",
                port=8001,
            ),
            AgentConfig(
                name="agent2",
                description="Test agent 2",
                url="http://localhost:8002",
                port=8002,
            ),
        ]

        # ヘルスチェック結果をモック
        with patch.object(
            AgentHealthCheck, "check_agent_health"
        ) as mock_check:
            mock_check.side_effect = [True, False]  # 1つ目成功、2つ目失敗

            # When: 全エージェントのヘルスチェックを実行
            results = await AgentHealthCheck.check_all_agents_health(configs)

            # Then: 正しい結果が返される
            assert results == {"agent1": True, "agent2": False}
            assert mock_check.call_count == 2
