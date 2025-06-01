"""
Gemini A2A Agent

Google Gemini 2.5 Pro を使用したA2Aエージェント
"""

import logging
from typing import Any, Dict, List

from a2a.types import AgentSkill

from ..utils.config import AgentConfig
from ..utils.gemini_client import GeminiAPIError, GeminiClient
from ..utils.gemini_config import GeminiConfig
from .base_agent import BaseA2AAgent

logger = logging.getLogger(__name__)


class GeminiA2AAgent(BaseA2AAgent):
    """Gemini 2.5 Pro を使用したA2Aエージェント"""

    # クラス定数
    MAX_CONTEXT_MESSAGES = 20  # 会話履歴の最大保持数（10往復分）
    MAX_INPUT_LENGTH = 10000  # ユーザー入力の最大長

    def __init__(
        self, config: AgentConfig, gemini_config: GeminiConfig
    ) -> None:
        """
        Args:
            config: A2Aエージェント設定
            gemini_config: Gemini API設定
        """
        super().__init__(config)
        self.gemini_config = gemini_config
        self.gemini_client = GeminiClient(gemini_config)
        self.conversation_context: List[str] = []

        # エージェント固有のログ設定
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.logger.info(
            f"Gemini agent initialized with model: {gemini_config.model}"
        )

    def get_skills(self) -> List[AgentSkill]:
        """エージェントのスキル一覧を取得"""
        return [
            AgentSkill(
                id="chat",
                name="intelligent_chat",
                description="Have an intelligent conversation using Gemini 2.5 Pro",
                tags=["conversation", "ai", "general"],
            ),
            AgentSkill(
                id="qa",
                name="question_answering",
                description="Answer questions using advanced AI capabilities",
                tags=["qa", "knowledge", "research"],
            ),
            AgentSkill(
                id="help",
                name="help_assistant",
                description="Provide help and guidance",
                tags=["help", "assistance", "guide"],
            ),
        ]

    def _handle_gemini_api_error(self, error: GeminiAPIError) -> str:
        """
        GeminiAPIErrorを分類して適切なユーザーメッセージを返す

        Args:
            error: GeminiAPIError例外

        Returns:
            ユーザーフレンドリーなエラーメッセージ
        """
        error_msg = str(error)

        if "SAFETY_FILTER" in error_msg:
            self.logger.warning(
                "🚨 Safety filter activated - adjusting response"
            )
            return (
                "申し訳ございませんが、安全性フィルターにより"
                "この内容についてお答えできません。"
                "別の質問をお試しください。"
            )
        elif "RECITATION_FILTER" in error_msg:
            self.logger.warning("🚨 Recitation filter activated")
            return (
                "申し訳ございませんが、著作権の観点から"
                "この内容についてお答えできません。"
            )
        elif "CONTENT_FILTER" in error_msg:
            self.logger.warning("🚨 Content filter activated")
            return (
                "申し訳ございませんが、内容フィルターにより"
                "この質問にはお答えできません。"
            )
        elif "APIキーが期限切れ" in error_msg:
            self.logger.error("🚨 API key expired")
            return (
                "システムエラー: APIキーが期限切れです。"
                "管理者にお問い合わせください。"
            )
        elif "使用制限" in error_msg:
            self.logger.warning("🚨 API quota exceeded")
            return (
                "一時的にサービスが混雑しています。"
                "しばらく時間をおいて再度お試しください。"
            )
        else:
            # その他のAPIエラー
            self.logger.error(f"🚨 Unclassified API error: {error_msg}")
            return (
                "申し訳ございません。AIサービスに一時的な問題が発生しています。"
                "しばらく時間をおいて再度お試しください。"
            )

    async def process_user_input(self, user_input: str) -> str:
        """
        ユーザー入力をGemini 2.5 Proで処理

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            Geminiが生成した応答テキスト
        """
        try:
            # 入力バリデーション
            sanitized_input = self._sanitize_user_input(user_input)

            # 特別なコマンドの処理
            if self._is_help_command(sanitized_input):
                return self._get_help_message()

            elif self._is_clear_command(sanitized_input):
                return self._clear_conversation_context()

            elif self._is_status_command(sanitized_input):
                return await self._get_status_message()

            # 通常の対話処理
            prompt = self._build_conversation_prompt(sanitized_input)
            self.logger.debug(f"最終的にAPIに送信されるプロンプト: {prompt}")
            response = await self.gemini_client.generate_response_with_timeout(
                prompt, timeout=15.0  # 5秒→15秒に延長
            )

            # 会話履歴を更新
            self._update_conversation_context(sanitized_input, response)

            return response

        except ValueError as e:
            self.logger.warning(f"Input validation error: {e}")
            return f"入力エラー: {e}"

        except GeminiAPIError as e:
            self.logger.error(f"Gemini API error: {e}")
            return self._handle_gemini_api_error(e)

        except Exception as e:
            self.logger.error(f"Unexpected error in process_user_input: {e}")
            return (
                "予期しない問題が発生しました。"
                "しばらく時間をおいて再度お試しください。"
            )

    def _sanitize_user_input(self, user_input: str) -> str:
        """ユーザー入力のサニタイズ"""
        if not user_input:
            raise ValueError("入力が空です")

        sanitized = user_input.strip()

        if len(sanitized) > self.MAX_INPUT_LENGTH:
            raise ValueError(
                f"入力が長すぎます（最大{self.MAX_INPUT_LENGTH}文字）"
            )

        return sanitized

    def _is_help_command(self, input_text: str) -> bool:
        """ヘルプコマンドかどうか判定"""
        return input_text.lower() in ["help", "?", "ヘルプ"]

    def _is_clear_command(self, input_text: str) -> bool:
        """クリアコマンドかどうか判定"""
        return input_text.lower() in ["clear", "クリア", "リセット"]

    def _is_status_command(self, input_text: str) -> bool:
        """ステータスコマンドかどうか判定"""
        return input_text.lower() in ["status", "ステータス", "状態"]

    def _build_conversation_prompt(self, user_input: str) -> str:
        """会話履歴を考慮したプロンプトを構築"""
        # base_prompt = ""  # ★一時的にシステムプロンプトを空にする (調査のため)
        # # base_prompt = (
        # #     "あなたは親切で知識豊富なAIアシスタントです。"
        # #     "ユーザーの質問に対して、正確で有用な回答を提供してください。"
        # #     "回答は分かりやすく、適度な長さで行ってください。\n\n"
        # # )

        # # 会話履歴があれば追加（最新6件=3往復分）
        # if self.conversation_context:
        #     recent_context = self.conversation_context[-6:]
        #     conversation_history = "\n".join(recent_context)
        #     # base_prompt が空なので、履歴がある場合は履歴から始まる
        #     if base_prompt:  # base_promptが空でない場合のみ改行を追加
        #         base_prompt += f"会話履歴:\n{conversation_history}\n\n"
        #     else:
        #         base_prompt = f"会話履歴:\n{conversation_history}\n\n"

        # base_prompt += f"ユーザー: {user_input}\nアシスタント: "

        # return base_prompt
        return user_input  # ★★★ 最もシンプルな形 (システムプロンプト、履歴、接頭辞/接尾辞なし)

    def _update_conversation_context(
        self, user_input: str, ai_response: str
    ) -> None:
        """会話履歴を更新"""
        self.conversation_context.extend(
            [f"User: {user_input}", f"Assistant: {ai_response}"]
        )

        # 上限を超えた場合は古い履歴を削除
        if len(self.conversation_context) > self.MAX_CONTEXT_MESSAGES:
            self.conversation_context = self.conversation_context[
                -self.MAX_CONTEXT_MESSAGES :
            ]

    def _clear_conversation_context(self) -> str:
        """会話履歴をクリア"""
        self.conversation_context.clear()
        return "✅ 会話履歴をクリアしました。新しい会話を始めましょう！"

    async def _get_status_message(self) -> str:
        """ステータスメッセージを生成"""
        health = await self.gemini_client.health_check()
        client_info = self.gemini_client.get_client_info()

        return (
            f"🤖 {self.config.name}\n"
            f"📡 URL: {self.config.url}\n"
            f"🧠 Model: {client_info['model']}\n"
            f"🌡️ Temperature: {client_info['temperature']}\n"
            f"📝 Max Tokens: {client_info['max_tokens']}\n"
            f"💚 Status: {'✅ OK' if health else '❌ ERROR'}\n"
            f"💬 Context: {len(self.conversation_context)} messages\n"
            f"🔑 API Key: {client_info['api_key_masked']}"
        )

    def _get_help_message(self) -> str:
        """ヘルプメッセージを生成"""
        return (
            f"🤖 **{self.config.name}** - Gemini 2.5 Pro搭載エージェント\n\n"
            "📝 **使い方:**\n"
            "• 質問やメッセージを自由に送信してください\n"
            "• `status` - エージェントの状態確認\n"
            "• `clear` - 会話履歴をクリア\n"
            "• `help` - このヘルプメッセージを表示\n\n"
            "🧠 **特徴:**\n"
            "• Google Gemini 2.5 Proによる高度な対話\n"
            "• 会話履歴を考慮した文脈理解\n"
            "• A2Aプロトコル完全準拠\n"
            "• リアルタイム応答\n\n"
            "💡 **技術仕様:**\n"
            f"• Model: {self.gemini_config.model}\n"
            f"• Temperature: {self.gemini_config.temperature}\n"
            f"• Max Context: {self.MAX_CONTEXT_MESSAGES // 2} 往復\n\n"
            "何でもお気軽にお聞かせください！✨"
        )

    def get_agent_stats(self) -> Dict[str, Any]:
        """エージェントの統計情報を取得"""
        return {
            "conversation_messages": len(self.conversation_context),
            "max_context_messages": self.MAX_CONTEXT_MESSAGES,
            "gemini_model": self.gemini_config.model,
            "gemini_temperature": self.gemini_config.temperature,
            "skills_count": len(self.get_skills()),
        }
