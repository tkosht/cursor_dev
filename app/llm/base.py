"""
LLMの基底クラス
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMMetrics(BaseModel):
    """LLMの実行メトリクス"""
    total_tokens: int = Field(default=0, description="合計トークン数")
    prompt_tokens: int = Field(default=0, description="プロンプトのトークン数")
    completion_tokens: int = Field(default=0, description="生成結果のトークン数")
    total_cost: float = Field(default=0.0, description="合計コスト")


class BaseLLM(ABC):
    """LLMの基底クラス"""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.1):
        """
        初期化

        Args:
            api_key (str): APIキー
            model (str): モデル名
            temperature (float, optional): 生成時の温度パラメータ. Defaults to 0.1.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.metrics = LLMMetrics()
        self._init_client()
    
    @abstractmethod
    def _init_client(self) -> None:
        """クライアントの初期化"""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        テキストを生成

        Args:
            prompt (str): ��ロンプト

        Returns:
            str: 生成されたテキスト
        """
        pass
    
    @abstractmethod
    async def analyze_content(self, content: str, task: str) -> Dict[str, Any]:
        """
        コンテンツを分析

        Args:
            content (str): 分析対象のコンテンツ
            task (str): 分析タスクの種類

        Returns:
            Dict[str, Any]: 分析結果
        """
        pass
    
    def update_metrics(self, prompt_tokens: int, completion_tokens: int, cost: float) -> None:
        """
        メトリクスを更新

        Args:
            prompt_tokens (int): プロンプトのトークン数
            completion_tokens (int): 生成結果のトークン数
            cost (float): コスト
        """
        self.metrics.prompt_tokens += prompt_tokens
        self.metrics.completion_tokens += completion_tokens
        self.metrics.total_tokens = self.metrics.prompt_tokens + self.metrics.completion_tokens
        self.metrics.total_cost += cost
    
    def get_metrics(self) -> LLMMetrics:
        """
        メトリクスを取得

        Returns:
            LLMMetrics: メトリクス
        """
        return self.metrics
    
    def reset_metrics(self) -> None:
        """メトリクスをリセット"""
        self.metrics = LLMMetrics() 