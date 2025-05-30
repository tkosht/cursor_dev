"""
Gemini AI Client Wrapper

Google Gemini API との通信を担当するクライアントクラス
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import google.generativeai as genai
from google.generativeai.types import (
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
)

from .gemini_config import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Gemini API 関連のエラー"""

    pass


class GeminiClient:
    """Gemini AI API のクライアントWrapper"""

    def __init__(self, config: GeminiConfig) -> None:
        """
        Args:
            config: Gemini API設定
        """
        self.config = config
        self._model: Optional[genai.GenerativeModel] = None
        self._initialized = False
        self._setup_client()

    def _setup_client(self) -> None:
        """Geminiクライアントをセットアップ"""
        try:
            # API認証設定
            genai.configure(api_key=self.config.api_key)

            # Safety settings
            safety_settings = self._get_safety_settings()

            # モデル初期化
            self._model = genai.GenerativeModel(
                model_name=self.config.model,
                generation_config=GenerationConfig(
                    **self.config.to_generation_config()
                ),
                safety_settings=safety_settings,
            )

            self._initialized = True
            logger.info(f"Gemini client initialized: {self.config.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Client initialization failed: {e}") from e

    def _get_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """セーフティ設定を取得"""
        if self.config.safety_settings:
            return self.config.safety_settings

        # デフォルトのセーフティ設定（簡略化）
        try:
            return {
                HarmCategory.HARM_CATEGORY_HARASSMENT: (
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: (
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: (
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: (
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
            }
        except AttributeError:
            # フォールバック：空の設定
            logger.warning(
                "Safety settings unavailable, using empty configuration"
            )
            return {}

    async def generate_response(self, prompt: str) -> str:
        """
        Geminiからレスポンスを生成

        Args:
            prompt: 入力プロンプト

        Returns:
            生成されたレスポンステキスト

        Raises:
            GeminiAPIError: API呼び出しに失敗した場合
        """
        if not self._initialized or not self._model:
            raise GeminiAPIError("Client not properly initialized")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # 非同期でAPI呼び出し
            response = await asyncio.to_thread(
                self._model.generate_content, prompt.strip()
            )

            if not response.text:
                logger.warning("Empty response from Gemini API")
                return "申し訳ございませんが、回答を生成できませんでした。"

            return response.text.strip()

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"Failed to generate response: {e}") from e

    async def generate_response_with_timeout(
        self, prompt: str, timeout: float = 5.0
    ) -> str:
        """
        タイムアウト付きでレスポンスを生成

        Args:
            prompt: 入力プロンプト
            timeout: タイムアウト時間（秒）

        Returns:
            生成されたレスポンステキスト
        """
        try:
            return await asyncio.wait_for(
                self.generate_response(prompt), timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Gemini API timeout after {timeout} seconds")
            return "応答時間が長すぎます。より簡潔な質問でお試しください。"
        except GeminiAPIError:
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"

    async def health_check(self) -> bool:
        """
        Gemini API の接続確認

        Returns:
            接続状態（True=正常, False=異常）
        """
        if not self._initialized:
            return False

        try:
            response = await self.generate_response_with_timeout(
                "Hello", timeout=3.0
            )
            return bool(
                response
                and len(response) > 0
                and "申し訳ございません" not in response
            )

        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False

    def get_client_info(self) -> Dict[str, Any]:
        """クライアント情報を取得"""
        return {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "initialized": self._initialized,
            "api_key_masked": self.config.get_masked_api_key(),
        }
