"""
LLM処理

LLMを使用した回答生成を行うモジュール
"""

import asyncio
from typing import Dict, List, Optional

import google.generativeai as genai
import ollama
from anthropic import Anthropic
from anthropic import APIError as AnthropicAPIError
from openai import APIError as OpenAIAPIError
from openai import OpenAI


class LLMProcessorError(Exception):
    """LLMProcessor固有のエラー"""

    pass


class LLMProcessor:
    """LLM処理クラス"""

    SUPPORTED_MODELS = {
        "gemini": "gemini-pro",
        "gpt": "gpt-4-turbo-preview",
        "claude": "claude-3-sonnet-20240229",
        "ollama": "mistral",
    }

    # モデルごとのトークン制限
    MAX_TOKENS = {
        "gemini": 30720,  # Gemini Pro
        "gpt": 128000,  # GPT-4 Turbo
        "claude": 200000,  # Claude 3 Sonnet
        "ollama": 8192,  # Mistral
    }

    # トークンあたりの平均文字数（日本語）
    CHARS_PER_TOKEN = 2

    def __init__(
        self, model_type: str = "gemini", api_key: Optional[str] = None
    ):
        """
        LLMProcessorの初期化

        Args:
            model_type: 使用するLLMの種類（デフォルト: gemini）
            api_key: API Key（必要な場合）

        Raises:
            LLMProcessorError: サポートされていないモデルタイプが指定された場合
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise LLMProcessorError(
                f"サポートされていないモデルタイプです: {model_type}"
            )

        self.model_type = model_type
        self.api_key = api_key
        self._setup_model()

    def _setup_model(self) -> None:
        """
        モデルのセットアップ

        Raises:
            LLMProcessorError: モデルの初期化に失敗した場合
        """
        try:
            setup_methods = {
                "gemini": self._setup_gemini,
                "gpt": self._setup_gpt,
                "claude": self._setup_claude,
                "ollama": self._setup_ollama,
            }

            setup_method = setup_methods.get(self.model_type)
            if not setup_method:
                raise LLMProcessorError(
                    f"サポートされていないモデルタイプです: {self.model_type}"
                )

            setup_method()
        except ValueError as e:
            raise LLMProcessorError(str(e))
        except OpenAIAPIError as e:
            if "invalid_api_key" in str(e):
                raise LLMProcessorError("APIキーが無効です")
            raise LLMProcessorError(f"OpenAI APIエラー: {e}")
        except AnthropicAPIError as e:
            if "invalid_api_key" in str(e):
                raise LLMProcessorError("APIキーが無効です")
            raise LLMProcessorError(f"Anthropic APIエラー: {e}")
        except Exception as e:
            if "Invalid API key" in str(e):
                raise LLMProcessorError("APIキーが無効です")
            raise LLMProcessorError(f"モデルの初期化に失敗しました: {e}")

    def _setup_gemini(self) -> None:
        """Geminiモデルのセットアップ"""
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            self.SUPPORTED_MODELS[self.model_type]
        )

    def _setup_gpt(self) -> None:
        """GPTモデルのセットアップ"""
        if not self.api_key:
            raise ValueError("APIキーが必要です")
        try:
            self.client = OpenAI(api_key=self.api_key)
            # APIキーの検証のため、簡単なAPI呼び出しを試みる
            self.client.models.list()
        except OpenAIAPIError as e:
            if "invalid_api_key" in str(e):
                raise ValueError("APIキーが無効です")
            raise e

    def _setup_claude(self) -> None:
        """Claudeモデルのセットアップ"""
        if not self.api_key:
            raise ValueError("APIキーが必要です")
        try:
            self.client = Anthropic(api_key=self.api_key)
            # APIキーの検証のため、簡単なAPI呼び出しを試みる
            self.client.messages.create(
                model=self.SUPPORTED_MODELS[self.model_type],
                max_tokens=1,
                content="test",
            )
        except AnthropicAPIError as e:
            if "invalid_api_key" in str(e):
                raise ValueError("APIキーが無効です")
            raise e

    def _setup_ollama(self) -> None:
        """Ollamaモデルのセットアップ"""
        self.client = ollama

    def _format_context(self, context: List[Dict]) -> str:
        """
        コンテキストをプロンプト用にフォーマット

        Args:
            context: 関連するブックマークのリスト

        Returns:
            str: フォーマットされたコンテキスト
        """
        return "\n\n".join(
            [
                f"Tweet: {bookmark['text']}\nURL: {bookmark.get('url', 'N/A')}"
                for bookmark in context
            ]
        )

    def _create_prompt(self, query: str, context: List[Dict]) -> str:
        """
        プロンプトを生成

        Args:
            query: ユーザーからのクエリ
            context: 関連するブックマークのリスト

        Returns:
            str: 生成されたプロンプト

        Raises:
            LLMProcessorError: プロンプトが長すぎる場合
        """
        context_text = self._format_context(context)
        prompt = f"""以下のブックマークされたツイートを参考に、質問に答えてください。

コンテキスト:
{context_text}

質問: {query}

回答形式:
1. 関連する情報を箇条書きで要約
2. 質問への直接的な回答
3. 参考にしたツイートのURL

回答:"""

        # プロンプトの長さをチェック
        estimated_tokens = len(prompt) / self.CHARS_PER_TOKEN
        if estimated_tokens > self.MAX_TOKENS[self.model_type]:
            raise LLMProcessorError(
                f"プロンプトが長すぎます（推定{int(estimated_tokens)}トークン）。"
                f"{self.model_type}の上限は{self.MAX_TOKENS[self.model_type]}トークンです。"
            )

        return prompt

    async def _generate_gemini_response(self, prompt: str) -> str:
        """Geminiモデルで回答を生成"""
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def _generate_gpt_response(self, prompt: str) -> str:
        """GPTモデルで回答を生成"""
        response = await self.client.chat.completions.create(
            model=self.SUPPORTED_MODELS[self.model_type],
            messages=[
                {
                    "role": "system",
                    "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    async def _generate_claude_response(self, prompt: str) -> str:
        """Claudeモデルで回答を生成"""
        response = await self.client.messages.create(
            model=self.SUPPORTED_MODELS[self.model_type],
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def _generate_ollama_response(self, prompt: str) -> str:
        """Ollamaモデルで回答を生成"""
        response = await self.client.chat(
            model=self.SUPPORTED_MODELS[self.model_type],
            messages=[
                {
                    "role": "system",
                    "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response["message"]["content"]

    async def _generate_model_response(self, prompt: str) -> str:
        """
        モデルタイプに応じた回答を生成

        Args:
            prompt: 生成用プロンプト

        Returns:
            str: 生成された回答

        Raises:
            LLMProcessorError: サポートされていないモデルタイプの場合
        """
        model_generators = {
            "gemini": self._generate_gemini_response,
            "gpt": self._generate_gpt_response,
            "claude": self._generate_claude_response,
            "ollama": self._generate_ollama_response,
        }

        generator = model_generators.get(self.model_type)
        if not generator:
            raise LLMProcessorError(
                f"サポートされていないモデルタイプです: {self.model_type}"
            )

        return await generator(prompt)

    async def generate_response(
        self, query: str, context: List[Dict], timeout: int = 30
    ) -> str:
        """
        クエリと文脈から回答を生成する

        Args:
            query: ユーザーからのクエリ
            context: 関連するブックマークのリスト
            timeout: タイムアウト秒数（デフォルト: 30秒）

        Returns:
            str: 生成された回答

        Raises:
            LLMProcessorError: 回答生成に失敗した場合
        """
        if not context:
            return "関連するブックマークが見つかりませんでした。"

        try:
            prompt = self._create_prompt(query, context)
            return await asyncio.wait_for(
                self._generate_model_response(prompt), timeout=timeout
            )

        except asyncio.TimeoutError:
            raise LLMProcessorError(
                f"回答生成がタイムアウトしました（制限時間: {timeout}秒）"
            )
        except (OpenAIAPIError, AnthropicAPIError) as e:
            if "rate limit" in str(e).lower():
                raise LLMProcessorError(
                    "APIのレート制限に達しました。しばらく待ってから再試行してください。"
                )
            elif "invalid api key" in str(e).lower():
                raise LLMProcessorError(
                    "APIキーが無効です。設定を確認してください。"
                )
            raise LLMProcessorError(f"API呼び出しに失敗しました: {e}")
        except Exception as e:
            raise LLMProcessorError(f"回答生成に失敗しました: {e}")
