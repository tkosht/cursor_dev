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

    def _check_finish_reason(self, response) -> None:
        """
        レスポンスのfinish_reasonをチェックしてエラーを発生させる

        Args:
            response: Gemini APIのレスポンス

        Raises:
            GeminiAPIError: finish_reasonに問題がある場合
        """
        if not (hasattr(response, "candidates") and response.candidates):
            return

        candidate = response.candidates[0]
        if not hasattr(candidate, "finish_reason"):
            return

        finish_reason = candidate.finish_reason
        if finish_reason == 2:  # SAFETY
            logger.warning("Content blocked by safety filters")
            raise GeminiAPIError(
                "SAFETY_FILTER: Content blocked by safety filters"
            )
        elif finish_reason == 3:  # RECITATION
            logger.warning("Content blocked for recitation")
            raise GeminiAPIError(
                "RECITATION_FILTER: Content blocked for recitation"
            )
        elif finish_reason == 4:  # OTHER
            logger.warning("Content blocked for other reasons")
            raise GeminiAPIError(
                "CONTENT_FILTER: Content blocked for other reasons"
            )

    def _extract_response_text(self, response) -> str:
        """
        レスポンスからテキストを安全に抽出

        Args:
            response: Gemini APIのレスポンス

        Returns:
            抽出されたテキスト
        """
        try:
            text = response.text
            if not text or not text.strip():
                logger.warning("Empty response from Gemini API")
                return "申し訳ございませんが、回答を生成できませんでした。"
            return text.strip()
        except AttributeError as attr_error:
            # response.text にアクセスできない場合
            logger.error(f"Cannot access response.text: {attr_error}")
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"
        except Exception as text_error:
            # その他のテキストアクセスエラー
            logger.error(f"Error accessing response text: {text_error}")
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"

    def _classify_api_error(self, error_message: str) -> str:
        """
        APIエラーを分類してユーザーフレンドリーなメッセージを生成

        Args:
            error_message: 元のエラーメッセージ

        Returns:
            分類されたエラーメッセージ
        """
        error_lower = error_message.lower()

        if (
            "api key expired" in error_lower
            or "api_key_invalid" in error_lower
        ):
            return "APIキーが期限切れまたは無効です。新しいAPIキーを取得してください。"
        elif "quota" in error_lower or "rate" in error_lower:
            return "APIの使用制限に達しました。しばらく待ってから再試行してください。"
        elif "permission" in error_lower or "forbidden" in error_lower:
            return "APIキーに必要な権限がありません。設定を確認してください。"
        elif "network" in error_lower or "connection" in error_lower:
            return "ネットワーク接続に問題があります。接続を確認してください。"
        else:
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"

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

            # finish_reason チェック
            self._check_finish_reason(response)

            # テキスト抽出
            return self._extract_response_text(response)

        except GeminiAPIError:
            # 既に適切にハンドリングされたエラーは再発生
            raise
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # APIエラーの分類とユーザーフレンドリーなメッセージ
            classified_message = self._classify_api_error(str(e))
            raise GeminiAPIError(classified_message) from e

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
