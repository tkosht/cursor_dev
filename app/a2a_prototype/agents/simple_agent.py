"""
Simple A2A Test Agent

BaseA2AAgentを継承したシンプルなテストエージェント
動作確認用の最小実装
"""

from typing import List

from a2a.types import AgentSkill

from ..utils.config import AgentConfig
from .base_agent import BaseA2AAgent


class SimpleTestAgent(BaseA2AAgent):
    """
    シンプルなテストエージェント

    基本的な会話と echo 機能を提供する
    """

    def get_skills(self) -> List[AgentSkill]:
        """エージェントのスキル一覧を取得"""
        return [
            AgentSkill(
                id="echo",
                name="echo",
                description="Echo back the user's message",
                tags=["text", "utility"],
            ),
            AgentSkill(
                id="greet",
                name="greet",
                description="Greet the user",
                tags=["conversation", "social"],
            ),
        ]

    async def process_user_input(self, user_input: str) -> str:
        """
        ユーザー入力を処理

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            エージェントの応答テキスト
        """
        # 簡単な処理ロジック
        input_lower = user_input.lower().strip()

        if input_lower.startswith("hello") or input_lower.startswith("hi"):
            return (
                f"Hello! I'm {self.config.name}. "
                "How can I help you today?"
            )

        elif input_lower.startswith("echo"):
            # "echo "を除去してそのまま返す
            message = user_input[5:].strip() if len(user_input) > 5 else ""
            return (
                f"Echo: {message}" if message
                else "Echo: (empty message)"
            )

        elif input_lower.startswith("status"):
            return (
                f"I'm {self.config.name} running on {self.config.url}. "
                "Status: OK"
            )

        elif input_lower in ["help", "?"]:
            return (
                f"Available commands for {self.config.name}:\n"
                "- hello/hi: Greet the agent\n"
                "- echo <message>: Echo back your message\n"
                "- status: Check agent status\n"
                "- help: Show this help message"
            )

        else:
            return (
                f"I received: '{user_input}'. "
                "Try 'help' for available commands."
            )


# テスト用のヘルパー関数
def create_test_agent(port: int = 8001) -> SimpleTestAgent:
    """
    テスト用のシンプルエージェントを作成

    Args:
        port: エージェントのポート番号

    Returns:
        設定済みのSimpleTestAgent
    """
    config = AgentConfig(
        name="simple-test-agent",
        description="A simple test agent for A2A protocol verification",
        url=f"http://localhost:{port}",
        port=port,
    )

    return SimpleTestAgent(config)


if __name__ == "__main__":
    """直接実行時のテスト"""
    import logging

    # ログレベルを設定
    logging.basicConfig(level=logging.INFO)

    # テストエージェントを作成
    agent = create_test_agent(8001)

    print(f"Starting {agent.config.name}...")
    print(f"Agent URL: {agent.config.url}")
    print(f"Agent Card: {agent.agent_card}")

    # エージェントを起動
    try:
        agent.run_agent()
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
