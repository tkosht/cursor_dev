"""
LLMの基底クラス
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LLMError(Exception):
    """LLMの基底エラー"""

    pass


class LLMConnectionError(LLMError):
    """LLM接続エラー"""

    pass


class LLMResponseError(LLMError):
    """LLMレスポンスエラー"""

    pass


class LLMMetrics(BaseModel):
    """LLMの実行メトリクス"""

    total_tokens: int = Field(default=0, description="合計トークン数")
    prompt_tokens: int = Field(default=0, description="プロンプトのトークン数")
    completion_tokens: int = Field(default=0, description="生成結果のトークン数")
    total_cost: float = Field(default=0.0, description="合計コスト")
    last_latency: float = Field(default=0.0, description="最後の実行のレイテンシ")


class BaseLLM(ABC):
    """LLMの基底クラス"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.1,
    ):
        """
        初期化

        Args:
            api_key (Optional[str]): APIキー
            model (Optional[str]): モデル名
            temperature (float): 生成時の温度パラメータ
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
            prompt (str): プロンプト

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
        start_time = time.monotonic()
        try:
            result = await self._analyze_content_impl(content, task)
            return result
        finally:
            end_time = time.monotonic()
            self.metrics.last_latency = end_time - start_time

    @abstractmethod
    async def _analyze_content_impl(self, content: str, task: str) -> Dict[str, Any]:
        """
        コンテンツ分析の実装

        Args:
            content (str): 分析対象のコンテンツ
            task (str): 分析タスクの種類

        Returns:
            Dict[str, Any]: 分析結果
        """
        pass

    def update_metrics(
        self, prompt_tokens: int, completion_tokens: int, cost: float
    ) -> None:
        """
        メトリクスを更新

        Args:
            prompt_tokens (int): プロンプトのトークン数
            completion_tokens (int): 生成結果のトークン数
            cost (float): コスト
        """
        self.metrics.prompt_tokens += prompt_tokens
        self.metrics.completion_tokens += completion_tokens
        self.metrics.total_tokens = (
            self.metrics.prompt_tokens + self.metrics.completion_tokens
        )
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

    def get_llm_latency(self) -> float:
        """
        最後のLLM実行のレイテンシを取得

        Returns:
            float: レイテンシ（秒）
        """
        return self.metrics.last_latency
