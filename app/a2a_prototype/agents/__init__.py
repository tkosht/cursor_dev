"""
A2A Prototype Agent 初期化モジュール
"""

from .base_agent import BaseA2AAgent
from .gemini_agent import GeminiA2AAgent
from .simple_agent import SimpleTestAgent


def create_gemini_agent(port: int = 8004, **kwargs) -> GeminiA2AAgent:
    """
    Geminiエージェントを作成

    Args:
        port: エージェントのポート番号
        **kwargs: 追加の設定パラメータ

    Returns:
        設定済みのGeminiA2AAgent

    Raises:
        ValueError: 環境変数が不足している場合
        GeminiConfigError: Gemini設定に問題がある場合
    """
    from ..utils.config import AgentConfig
    from ..utils.gemini_config import GeminiConfig

    # A2Aエージェント設定
    agent_config = AgentConfig(
        name=kwargs.get("name", "gemini-chat-agent"),
        description=kwargs.get(
            "description", "Advanced conversational AI agent powered by Gemini 2.5 Pro"
        ),
        url=f"http://localhost:{port}",
        port=port,
        version=kwargs.get("version", "1.0.0"),
    )

    # Gemini設定（環境変数から読み込み）
    gemini_config = GeminiConfig.from_env()

    # カスタム設定の上書き
    if "temperature" in kwargs:
        gemini_config.temperature = kwargs["temperature"]
    if "max_tokens" in kwargs:
        gemini_config.max_tokens = kwargs["max_tokens"]
    if "model" in kwargs:
        gemini_config.model = kwargs["model"]

    return GeminiA2AAgent(agent_config, gemini_config)


__all__ = ["BaseA2AAgent", "SimpleTestAgent", "GeminiA2AAgent", "create_gemini_agent"]
