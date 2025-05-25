"""
A2A Base Agent

全A2Aエージェントの基底クラス
python-a2aライブラリを使用したA2A準拠の実装
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from python_a2a import A2AServer, AgentCard, AgentSkill, TaskState, run_server

from ..utils.config import AgentConfig

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseA2AAgent(A2AServer, ABC):
    """A2Aエージェントの基底クラス"""

    def __init__(self, config: AgentConfig):
        """
        基底エージェントの初期化

        Args:
            config: エージェント設定
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")

        # エージェントカードを作成
        agent_card = AgentCard(
            name=config.name,
            description=config.description,
            url=config.url,
            version=config.version,
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
            },
            default_input_modes=["text"],
            default_output_modes=["text"],
            skills=self.get_skills(),
        )

        # A2Aサーバーの初期化
        super().__init__(agent_card=agent_card)

        self.logger.info(f"Initializing {config.name} at {config.url}")

    @abstractmethod
    def get_skills(self) -> List[AgentSkill]:
        """
        エージェントのスキル一覧を取得

        Returns:
            AgentSkillのリスト
        """
        pass

    def handle_task(self, task) -> Any:
        """
        タスクを処理する（A2AServerのメソッドをオーバーライド）

        Args:
            task: 処理するタスク

        Returns:
            処理結果
        """
        try:
            # タスクからテキストを抽出
            text = self.extract_text_from_task(task)

            if not text:
                task.status = TaskState.INPUT_REQUIRED
                return task

            # 具体的な処理は子クラスで実装
            return self.process_task_text(task, text)

        except Exception as e:
            self.logger.error(f"Task processing failed: {e}")
            task.status = TaskState.FAILED
            return task

    @abstractmethod
    def process_task_text(self, task, text: str) -> Any:
        """
        テキストを使ったタスク処理（子クラスで実装）

        Args:
            task: 処理するタスク
            text: 抽出されたテキスト

        Returns:
            処理されたタスク
        """
        pass

    def extract_text_from_task(self, task) -> str:
        """タスクからテキストを抽出"""
        try:
            if not (hasattr(task, "message") and task.message):
                return ""

            # content形式をチェック
            content_text = self._extract_from_content(task.message)
            if content_text:
                return content_text

            # parts形式をチェック
            return self._extract_from_parts(task.message)

        except Exception as e:
            self.logger.warning(f"Failed to extract text from task: {e}")
            return ""

    def _extract_from_content(self, message) -> str:
        """メッセージのcontentからテキストを抽出"""
        if not hasattr(message, "content"):
            return ""

        if isinstance(message.content, str):
            return message.content
        elif hasattr(message.content, "text"):
            return message.content.text

        return ""

    def _extract_from_parts(self, message) -> str:
        """メッセージのpartsからテキストを抽出"""
        if not (hasattr(message, "parts") and message.parts):
            return ""

        text_parts = []
        for part in message.parts:
            if hasattr(part, "text"):
                text_parts.append(part.text)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])

        return " ".join(text_parts)

    def run_agent(self):
        """エージェントを起動"""
        self.logger.info(
            f"Starting {self.config.name} on port {self.config.port}"
        )
        try:
            run_server(self, port=self.config.port, host=self.config.host)
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
