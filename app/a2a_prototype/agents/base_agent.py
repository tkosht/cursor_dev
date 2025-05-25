"""
A2A Base Agent

全A2Aエージェントの基底クラス
Google公式a2a-sdkライブラリを使用したA2A準拠の実装
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List

from a2a.server import A2AStarletteApplication, AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill, TaskState
from a2a.utils import new_agent_text_message

from ..utils.config import AgentConfig

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseA2AAgent(AgentExecutor, ABC):
    """A2Aエージェントの基底クラス（Google公式SDK使用）"""

    def __init__(self, config: AgentConfig):
        """
        基底エージェントの初期化

        Args:
            config: エージェント設定
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")

        # エージェントカードを作成
        self.agent_card = AgentCard(
            name=config.name,
            description=config.description,
            url=config.url,
            version=config.version,
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
            },
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=self.get_skills(),
        )

        self.logger.info(f"Initializing {config.name} at {config.url}")

    @abstractmethod
    def get_skills(self) -> List[AgentSkill]:
        """
        エージェントのスキル一覧を取得

        Returns:
            AgentSkillのリスト
        """
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        タスクを実行する（A2A公式SDKのメソッド）

        Args:
            context: リクエストコンテキスト
            event_queue: イベントキュー
        """
        try:
            # ユーザーメッセージからテキストを抽出
            user_input = context.get_user_input()

            if not user_input:
                # 入力が必要な状態に設定
                task = context.current_task
                task.status.state = TaskState.input_required
                await event_queue.enqueue_event(task)
                return

            # 具体的な処理は子クラスで実装
            response_text = await self.process_user_input(user_input)

            # エージェントの応答メッセージを作成
            agent_message = new_agent_text_message(response_text)

            # タスクを完了状態に設定
            task = context.current_task
            task.status.state = TaskState.completed
            task.history.append(agent_message)

            await event_queue.enqueue_event(task)

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            # タスクを失敗状態に設定
            task = context.current_task
            task.status.state = TaskState.failed
            await event_queue.enqueue_event(task)

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """
        タスクをキャンセルする

        Args:
            context: リクエストコンテキスト
            event_queue: イベントキュー
        """
        try:
            task = context.current_task
            task.status.state = TaskState.canceled
            await event_queue.enqueue_event(task)
            self.logger.info(f"Task {context.task_id} cancelled")
        except Exception as e:
            self.logger.error(f"Task cancellation failed: {e}")

    @abstractmethod
    async def process_user_input(self, user_input: str) -> str:
        """
        ユーザー入力を処理（子クラスで実装）

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            エージェントの応答テキスト
        """
        pass

    def create_app(self) -> A2AStarletteApplication:
        """
        A2A Starletteアプリケーションを作成

        Returns:
            設定済みのA2AStarletteApplication
        """
        app = A2AStarletteApplication(
            agent_card=self.agent_card,
            agent_executor=self
        )
        return app

    def run_agent(self, host: str = "0.0.0.0", port: int = None):
        """エージェントを起動"""
        if port is None:
            port = self.config.port

        self.logger.info(
            f"Starting {self.config.name} on port {port}"
        )
        try:
            app = self.create_app()
            starlette_app = app.build()

            import uvicorn
            uvicorn.run(starlette_app, host=host, port=port)
        except Exception as e:
            self.logger.error(f"Failed to start agent: {e}")
            raise


class AgentHealthCheck:
    """エージェントのヘルスチェック機能"""

    @staticmethod
    async def check_agent_health(agent_url: str, timeout: float = 5.0) -> bool:
        """
        エージェントのヘルス状態を確認

        Args:
            agent_url: エージェントのURL
            timeout: タイムアウト時間

        Returns:
            健康状態（True=正常, False=異常）
        """
        try:
            import httpx

            async with httpx.AsyncClient(timeout=timeout) as client:
                # エージェントカードを取得してヘルスチェック
                response = await client.get(
                    f"{agent_url}/.well-known/agent.json"
                )
                return response.status_code == 200

        except Exception as e:
            logger.warning(f"Health check failed for {agent_url}: {e}")
            return False

    @staticmethod
    async def check_all_agents_health(
        agent_configs: List[AgentConfig],
    ) -> Dict[str, bool]:
        """
        全エージェントのヘルス状態を確認

        Args:
            agent_configs: エージェント設定のリスト

        Returns:
            {agent_name: health_status}の辞書
        """
        health_results = {}

        for config in agent_configs:
            health_results[config.name] = (
                await AgentHealthCheck.check_agent_health(config.url)
            )

        return health_results
