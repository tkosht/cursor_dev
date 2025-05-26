"""
A2A Agent Configuration

エージェントの設定情報を管理するクラス
"""

from dataclasses import dataclass


@dataclass
class AgentConfig:
    """
    A2Aエージェントの設定情報
    """

    name: str
    description: str
    url: str
    port: int
    version: str = "1.0.0"

    def __post_init__(self):
        """設定値のバリデーション"""
        if not self.name:
            raise ValueError("Agent name is required")
        if not self.description:
            raise ValueError("Agent description is required")
        if not self.url:
            raise ValueError("Agent URL is required")
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("Port must be a positive integer")


# プリセット設定
class AgentPresets:
    """よく使用されるエージェント設定のプリセット"""

    @staticmethod
    def weather_agent(port: int = 8001) -> AgentConfig:
        """天気情報エージェントの設定"""
        return AgentConfig(
            name="weather-agent",
            description="Provides current weather information and forecasts",
            url=f"http://localhost:{port}",
            port=port,
        )

    @staticmethod
    def chat_agent(port: int = 8002) -> AgentConfig:
        """チャットエージェントの設定"""
        return AgentConfig(
            name="chat-agent",
            description="Simple conversational AI agent",
            url=f"http://localhost:{port}",
            port=port,
        )

    @staticmethod
    def calculator_agent(port: int = 8003) -> AgentConfig:
        """計算エージェントの設定"""
        return AgentConfig(
            name="calculator-agent",
            description="Performs mathematical calculations",
            url=f"http://localhost:{port}",
            port=port,
        )
