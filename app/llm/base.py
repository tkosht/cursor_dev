"""
LLMの基底クラス
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class LLMMetrics:
    """LLMの使用メトリクス"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    error_count: int = 0


class BaseLLM(ABC):
    """LLMの基底クラス"""

    def __init__(self, api_key: str, model: str = "default", temperature: float = 0.1):
        """初期化

        Args:
            api_key: APIキー
            model: モデル名
            temperature: 生成時の温度パラメータ
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.metrics = LLMMetrics()

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """テキストを生成

        Args:
            prompt: プロンプト

        Returns:
            生成されたテキスト
        """
        pass

    def update_metrics(
        self, prompt_tokens: int, completion_tokens: int, cost: float
    ) -> None:
        """メトリクスを更新

        Args:
            prompt_tokens: プロンプトのトークン数
            completion_tokens: 生成されたテキストのトークン数
            cost: コスト
        """
        self.metrics.prompt_tokens += prompt_tokens
        self.metrics.completion_tokens += completion_tokens
        self.metrics.total_tokens += prompt_tokens + completion_tokens
        self.metrics.total_cost += cost

    def get_metrics(self) -> Dict[str, float]:
        """メトリクスを取得

        Returns:
            メトリクス情報
        """
        return {
            "prompt_tokens": self.metrics.prompt_tokens,
            "completion_tokens": self.metrics.completion_tokens,
            "total_tokens": self.metrics.total_tokens,
            "total_cost": self.metrics.total_cost,
            "error_count": self.metrics.error_count,
        }

    def reset_metrics(self) -> None:
        """メトリクスをリセット"""
        self.metrics = LLMMetrics()
