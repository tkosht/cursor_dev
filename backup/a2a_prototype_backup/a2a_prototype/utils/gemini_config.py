"""
Gemini LLM Configuration

Google Gemini API の設定管理クラス
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class GeminiConfig:
    """Gemini API の設定情報を管理するデータクラス"""

    api_key: str
    model: str = "gemini-2.5-pro-preview-05-06"
    temperature: float = 0.7
    max_tokens: int = 1000
    safety_settings: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """設定値のバリデーション"""
        self._validate_api_key()
        self._validate_temperature()
        self._validate_max_tokens()
        self._validate_model()

    def _validate_api_key(self) -> None:
        """APIキーのバリデーション"""
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(self.api_key) < 10:  # 最低限の長さチェック
            raise ValueError("API key appears to be invalid (too short)")

    def _validate_temperature(self) -> None:
        """Temperatureパラメータのバリデーション"""
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("Temperature must be a number")
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")

    def _validate_max_tokens(self) -> None:
        """Max tokensパラメータのバリデーション"""
        if not isinstance(self.max_tokens, int):
            raise ValueError("Max tokens must be an integer")
        if not 1 <= self.max_tokens <= 8192:  # Gemini制限に基づく
            raise ValueError("Max tokens must be between 1 and 8192")

    def _validate_model(self) -> None:
        """モデル名のバリデーション"""
        if not self.model or not isinstance(self.model, str):
            raise ValueError("Model must be a non-empty string")
        # 利用可能なGeminiモデル一覧（2025年5月時点）
        valid_models = [
            # Gemini 2.5シリーズ（最新・推奨）
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.5-flash-preview-native-audio-dialog",
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-pro-preview-tts",
            # Gemini 2.0シリーズ
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash-preview-image-generation",
            "gemini-2.0-flash-live-001",
            # Gemini 1.5シリーズ（安定版）
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            # 旧形式（後方互換性のため）
            "gemini-2.5-pro",
            "gemini-1.0-pro",
        ]
        if self.model not in valid_models:
            # 警告は出すが、新しいモデルの可能性もあるのでエラーにはしない
            logger.warning(
                f"Unknown model: {self.model}. Valid models: {valid_models}"
            )

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        """環境変数から設定を読み込み"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000")),
        )

    def to_generation_config(self) -> Dict[str, Any]:
        """Gemini GenerationConfig形式に変換"""
        return {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }

    def get_masked_api_key(self) -> str:
        """マスキングされたAPIキーを取得（ログ出力用）"""
        if len(self.api_key) <= 8:
            return "*" * len(self.api_key)
        return f"{self.api_key[:8]}{'*' * (len(self.api_key) - 8)}"
