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
            safety_settings_to_use = self._get_safety_settings()
            logger.info(f"実際に使用されるセーフティ設定 (in _setup_client): {safety_settings_to_use}")

            # モデル初期化
            self._model = genai.GenerativeModel(
                model_name=self.config.model,
                generation_config=GenerationConfig(
                    **self.config.to_generation_config()
                ),
                safety_settings=safety_settings_to_use,
            )

            self._initialized = True
            logger.info(f"Gemini client initialized: {self.config.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Client initialization failed: {e}") from e

    def _get_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """セーフティ設定を取得"""
        if self.config.safety_settings:
            logger.debug(f"設定ファイルからセーフティ設定を使用: {self.config.safety_settings}")
            return self.config.safety_settings

        # デフォルトのセーフティ設定（簡略化）
        logger.debug("デフォルトのセーフティ設定を使用")
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
        # 詳細なレスポンス構造ログ
        logger.debug(
            f"Checking response structure: "
            f"hasattr candidates={hasattr(response, 'candidates')}"
        )

        if not (hasattr(response, "candidates") and response.candidates):
            logger.warning("Response has no candidates - empty response")
            return

        candidate = response.candidates[0]
        logger.debug(
            f"Candidate structure: "
            f"hasattr finish_reason={hasattr(candidate, 'finish_reason')}"
        )

        if not hasattr(candidate, "finish_reason"):
            logger.warning("Candidate has no finish_reason attribute")
            return

        logger.debug(f"Candidate object dir: {dir(candidate)}")
        if hasattr(candidate, "content"):
            logger.debug(f"Candidate content dir: {dir(candidate.content)}")
            if hasattr(candidate.content, "parts"):
                logger.debug(f"Candidate content parts: {candidate.content.parts}")

        finish_reason = candidate.finish_reason
        logger.info(
            f"🔍 FINISH_REASON DETECTED: {finish_reason} "
            f"(type: {type(finish_reason)})"
        )

        # 追加の詳細情報取得
        if hasattr(candidate, "safety_ratings"):
            logger.debug(f"Safety ratings: {candidate.safety_ratings}")
        if hasattr(response, "prompt_feedback"):
            logger.debug(f"Prompt feedback: {response.prompt_feedback}")

        if finish_reason == 2:  # SAFETY
            logger.error(
                "🚨 SAFETY FILTER TRIGGERED - Content blocked by safety filters"
            )
            logger.info(
                "📝 Safety filter details: finish_reason=2 indicates "
                "harmful content detection"
            )
            raise GeminiAPIError(
                "SAFETY_FILTER: Content blocked by safety filters"
            )
        elif finish_reason == 3:  # RECITATION
            logger.error(
                "🚨 RECITATION FILTER TRIGGERED - Content blocked for recitation"
            )
            logger.info(
                "📝 Recitation filter details: finish_reason=3 indicates "
                "copyright content"
            )
            raise GeminiAPIError(
                "RECITATION_FILTER: Content blocked for recitation"
            )
        elif finish_reason == 4:  # OTHER
            logger.error(
                "🚨 OTHER FILTER TRIGGERED - Content blocked for other reasons"
            )
            logger.info(
                "📝 Other filter details: finish_reason=4 indicates "
                "unspecified blocking"
            )
            raise GeminiAPIError(
                "CONTENT_FILTER: Content blocked for other reasons"
            )
        elif finish_reason == 1:  # STOP (normal completion)
            logger.debug("✅ Normal completion: finish_reason=1 (STOP)")
        else:
            logger.warning(
                f"⚠️ Unknown finish_reason: {finish_reason} - "
                f"proceeding with caution"
            )

    def _extract_response_text(self, response) -> str:
        """
        レスポンスからテキストを安全に抽出

        Args:
            response: Gemini APIのレスポンス

        Returns:
            抽出されたテキスト
        """
        logger.debug("🔍 Attempting to extract response text")

        try:
            text = response.text
            if not text or not text.strip():
                logger.warning("📝 Empty response text from Gemini API")
                logger.debug(
                    f"Response text details: text='{text}', "
                    f"length={len(text) if text else 0}"
                )
                return "申し訳ございませんが、回答を生成できませんでした。"

            logger.info(
                f"✅ Successfully extracted response text "
                f"(length: {len(text.strip())})"
            )
            return text.strip()

        except AttributeError as attr_error:
            # response.text にアクセスできない場合
            logger.error(f"🚨 Cannot access response.text: {attr_error}")
            logger.debug(f"Response object type: {type(response)}")
            has_dict = hasattr(response, "__dict__")
            logger.debug(
                f"Response attributes: "
                f"{dir(response) if has_dict else 'No __dict__'}"
            )
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"

        except Exception as text_error:
            # その他のテキストアクセスエラー
            logger.error(f"🚨 Error accessing response text: {text_error}")
            logger.debug(f"Error type: {type(text_error)}")
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

    def _log_api_request_details(self, prompt: str) -> None:
        """API呼び出し前の詳細情報をログ出力"""
        logger.info("🚀 Starting Gemini API call")
        logger.debug(f"📝 Prompt length: {len(prompt.strip())}")
        logger.debug(f"🔧 Model: {self.config.model}")
        logger.debug(f"🌡️ Temperature: {self.config.temperature}")
        logger.debug(f"📏 Max tokens: {self.config.max_tokens}")
        logger.debug(
            f"🔑 API key (masked): {self.config.get_masked_api_key()}"
        )
        logger.debug(f"✅ Client initialized: {self._initialized}")

    def _log_api_response_details(self, response) -> None:
        """API呼び出し後のレスポンス詳細をログ出力"""
        logger.info("✅ API call completed, analyzing response...")

        logger.debug(f"📦 Response type: {type(response)}")
        logger.debug(f"📦 Response attributes: {dir(response)}")

        if hasattr(response, "candidates"):
            candidate_count = (
                len(response.candidates) if response.candidates else 0
            )
            logger.debug(f"👥 Candidates count: {candidate_count}")

            if response.candidates:
                candidate = response.candidates[0]
                logger.debug(f"🎯 Candidate type: {type(candidate)}")
                logger.debug(f"🎯 Candidate attributes: {dir(candidate)}")

                if hasattr(candidate, "finish_reason"):
                    logger.info(
                        f"🏁 Raw finish_reason value: {candidate.finish_reason}"
                    )
                    logger.debug(
                        f"🏁 Finish_reason type: {type(candidate.finish_reason)}"
                    )

                if hasattr(candidate, "content"):
                    logger.debug(
                        f"📄 Content available: {candidate.content is not None}"
                    )

        if hasattr(response, "prompt_feedback"):
            logger.debug(f"💬 Prompt feedback: {response.prompt_feedback}")

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
        # ★実験: API呼び出しの都度クライアントを再セットアップ（モデルを再初期化）
        # これにより minimal_gemini_test.py の挙動に近づける試み
        logger.debug("実験的措置: generate_responseの度にクライアントを再セットアップします。")
        self._setup_client()  # モデルを再初期化

        if not self._initialized or not self._model:
            raise GeminiAPIError("Client not properly initialized after re-setup")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # 詳細ログ: API呼び出し前状態
        self._log_api_request_details(prompt)

        try:
            logger.info("📡 Executing generate_content_async API call...")

            # 非同期でAPI呼び出し (SDKのネイティブ非同期メソッドを使用)
            response = await self._model.generate_content_async(prompt.strip())

            # 詳細ログ: レスポンス分析
            self._log_api_response_details(response)

            # finish_reason チェック
            self._check_finish_reason(response)

            # テキスト抽出
            return self._extract_response_text(response)

        except GeminiAPIError:
            # 既に適切にハンドリングされたエラーは再発生
            logger.warning("⚠️ GeminiAPIError caught, re-raising...")
            raise
        except Exception as e:
            logger.error(f"🚨 Unexpected API error: {e}")
            logger.error(f"🚨 Error type: {type(e)}")
            logger.error(f"🚨 Error args: {e.args}")

            # 例外の詳細情報取得
            import traceback

            logger.debug(f"🔍 Full traceback: {traceback.format_exc()}")

            # APIエラーの分類とユーザーフレンドリーなメッセージ
            classified_message = self._classify_api_error(str(e))
            logger.info(f"📋 Classified error message: {classified_message}")
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
        logger.info(f"⏱️ Starting API call with timeout: {timeout} seconds")
        start_time = asyncio.get_event_loop().time()

        try:
            return await asyncio.wait_for(
                self.generate_response(prompt), timeout=timeout
            )
        except asyncio.TimeoutError:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                f"🚨 API TIMEOUT DETAILS:"
                f"\n  - Timeout setting: {timeout} seconds"
                f"\n  - Actual elapsed: {elapsed_time:.2f} seconds"
                f"\n  - Model: {self.config.model}"
                f"\n  - Prompt length: {len(prompt)}"
                f"\n  - Temperature: {self.config.temperature}"
            )
            return (
                f"応答時間が長すぎます（{elapsed_time:.1f}秒）。"
                f"より簡潔な質問でお試しください。"
            )
        except GeminiAPIError as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.warning(
                f"⚠️ GeminiAPIError (after {elapsed_time:.2f}s, re-raising): {e}"
            )
            raise

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
                "今日の日本の首都はどこですか？", timeout=10.0
            )
            return bool(
                response
                and len(response) > 0
                and "申し訳ございません" not in response
            )

        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False

    async def generate_response_for_diagnosis(self, prompt: str, timeout: float = 20.0) -> Any:
        """
        診断用に、Geminiからの生のAPIレスポンスオブジェクト全体を返す。
        タイムアウト付き。

        Args:
            prompt: 入力プロンプト
            timeout: タイムアウト時間（秒）

        Returns:
            Gemini APIからの生のレスポンスオブジェクト、またはタイムアウト/エラー時はNone
        """
        prompt_snippet = prompt[:30]
        logger.info(
            f"⏱️ [DIAGNOSIS] Starting API call with timeout: {timeout}s "
            f"for prompt: {prompt_snippet}..."
        )
        # 実験的措置として、呼び出し都度クライアントを再セットアップする部分は一旦コメントアウトし、
        # __init__で初期化された単一のモデルインスタンスを使用する標準的な方法に戻します。
        # logger.debug("[DIAGNOSIS] (Skipping re-setup for this diagnostic method)")
        # # self._setup_client()  # モデルを再初期化する実験的措置はここでは一旦保留

        if not self._initialized or not self._model:
            logger.error("[DIAGNOSIS] Client not properly initialized.")
            raise GeminiAPIError("Client not properly initialized for diagnosis")

        if not prompt or not prompt.strip():
            logger.error("[DIAGNOSIS] Prompt cannot be empty for diagnosis.")
            raise ValueError("Prompt cannot be empty for diagnosis")

        self._log_api_request_details(prompt)

        try:
            logger.info("📡 [DIAGNOSIS] Executing generate_content_async API call...")
            # SDKのネイティブ非同期メソッドを使用
            api_response = await asyncio.wait_for(
                self._model.generate_content_async(prompt.strip()),
                timeout=timeout
            )
            self._log_api_response_details(api_response)
            # ★診断のため、_check_finish_reason を呼び出してみる
            try:
                self._check_finish_reason(api_response)
            except GeminiAPIError as e:
                logger.warning(f"[DIAGNOSIS] chk_fin_reason: {e}") # メッセージを短縮
            return api_response
        except asyncio.TimeoutError:
            logger.error(f"🚨 [DIAGNOSIS] API TIMEOUT for prompt: {prompt_snippet}...")
            return None
        except Exception as e:
            logger.error(
                f"🚨 [DIAGNOSIS] Unexpected API error for prompt: {prompt_snippet}... "
                f"Error: {type(e).__name__} - {e}"
            )
            import traceback
            logger.debug(f"🔍 [DIAGNOSIS] Full traceback: {traceback.format_exc()}")
            return None

    def get_client_info(self) -> Dict[str, Any]:
        """クライアント情報を取得"""
        return {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "initialized": self._initialized,
            "api_key_masked": self.config.get_masked_api_key(),
        }
