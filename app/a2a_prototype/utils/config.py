"""
A2A Prototype Configuration

エージェント、ポート、URL等の設定管理
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class AgentConfig:
    """個別エージェントの設定"""
    name: str
    description: str
    port: int
    host: str = "localhost"
    version: str = "1.0.0"
    
    @property
    def url(self) -> str:
        """エージェントのURLを取得"""
        return f"http://{self.host}:{self.port}"
    
    @property
    def base_url(self) -> str:
        """ベースURLを取得（プロトコルとホスト:ポート）"""
        return self.url


class A2AConfig:
    """A2Aプロトタイプ全体の設定"""
    
    # エージェント設定
    WEATHER_AGENT = AgentConfig(
        name="weather_agent",
        description="天気情報を提供するA2Aエージェント",
        port=8001
    )
    
    CALCULATOR_AGENT = AgentConfig(
        name="calculator_agent", 
        description="数学計算を実行するA2Aエージェント",
        port=8002
    )
    
    ORCHESTRATOR_AGENT = AgentConfig(
        name="orchestrator_agent",
        description="複数エージェントを調整するオーケストレーター",
        port=8003
    )
    
    # レジストリ設定
    REGISTRY_CONFIG = AgentConfig(
        name="agent_registry",
        description="A2Aエージェント発見・管理レジストリ",
        port=8000
    )
    
    # 全エージェント一覧
    ALL_AGENTS = [
        WEATHER_AGENT,
        CALCULATOR_AGENT, 
        ORCHESTRATOR_AGENT
    ]
    
    # A2A プロトコル設定
    A2A_VERSION = "1.0.0"
    JSON_RPC_VERSION = "2.0"
    
    # 認証設定（デモ用）
    DEFAULT_AUTH_SCHEMES = ["Bearer"]
    DEMO_API_KEY = os.getenv("A2A_DEMO_API_KEY", "demo_api_key_12345")
    
    # モダリティ設定
    DEFAULT_INPUT_MODES = ["text", "text/plain"]
    DEFAULT_OUTPUT_MODES = ["text", "text/plain"]
    
    # タイムアウト設定
    REQUEST_TIMEOUT = 30
    AGENT_DISCOVERY_TIMEOUT = 10
    
    @classmethod
    def get_agent_by_name(cls, name: str) -> AgentConfig:
        """名前でエージェント設定を取得"""
        for agent in cls.ALL_AGENTS:
            if agent.name == name:
                return agent
        raise ValueError(f"Agent '{name}' not found")
    
    @classmethod
    def get_agent_urls(cls) -> Dict[str, str]:
        """全エージェントのURL辞書を取得"""
        return {agent.name: agent.url for agent in cls.ALL_AGENTS}
    
    @classmethod
    def get_registry_url(cls) -> str:
        """レジストリのURLを取得"""
        return cls.REGISTRY_CONFIG.url 