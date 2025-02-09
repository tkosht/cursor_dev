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
        "ollama": "mistral"
    }

    def __init__(self, model_type: str = "gemini", api_key: Optional[str] = None):
        """
        LLMProcessorの初期化

        Args:
            model_type: 使用するLLMの種類（デフォルト: gemini）
            api_key: API Key（必要な場合）

        Raises:
            LLMProcessorError: サポートされていないモデルタイプが指定された場合
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise LLMProcessorError(f"サポートされていないモデルタイプです: {model_type}")

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
            if self.model_type == "gemini":
                if self.api_key:
                    genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.SUPPORTED_MODELS[self.model_type])
            elif self.model_type == "gpt":
                self.client = OpenAI(api_key=self.api_key)
            elif self.model_type == "claude":
                self.client = Anthropic(api_key=self.api_key)
            elif self.model_type == "ollama":
                self.client = ollama
        except Exception as e:
            raise LLMProcessorError(f"モデルの初期化に失敗しました: {e}")

    def _format_context(self, context: List[Dict]) -> str:
        """
        コンテキストをプロンプト用にフォーマット

        Args:
            context: 関連するブックマークのリスト

        Returns:
            str: フォーマットされたコンテキスト
        """
        return "\n\n".join([
            f"Tweet: {bookmark['text']}\nURL: {bookmark.get('url', 'N/A')}"
            for bookmark in context
        ])

    def _create_prompt(self, query: str, context: List[Dict]) -> str:
        """
        プロンプトを生成

        Args:
            query: ユーザーからのクエリ
            context: 関連するブックマークのリスト

        Returns:
            str: 生成されたプロンプト
        """
        context_text = self._format_context(context)
        return f"""以下のブックマークされたツイートを参考に、質問に答えてください。

コンテキスト:
{context_text}

質問: {query}

回答形式:
1. 関連する情報を箇条書きで要約
2. 質問への直接的な回答
3. 参考にしたツイートのURL

回答:"""

    async def _generate_gemini_response(self, prompt: str) -> str:
        """Geminiモデルで回答を生成"""
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def _generate_gpt_response(self, prompt: str) -> str:
        """GPTモデルで回答を生成"""
        response = await self.client.chat.completions.create(
            model=self.SUPPORTED_MODELS[self.model_type],
            messages=[
                {"role": "system", "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def _generate_claude_response(self, prompt: str) -> str:
        """Claudeモデルで回答を生成"""
        response = await self.client.messages.create(
            model=self.SUPPORTED_MODELS[self.model_type],
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    async def _generate_ollama_response(self, prompt: str) -> str:
        """Ollamaモデルで回答を生成"""
        response = await self.client.chat(
            model=self.SUPPORTED_MODELS[self.model_type],
            messages=[
                {"role": "system", "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']

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
            "ollama": self._generate_ollama_response
        }

        generator = model_generators.get(self.model_type)
        if not generator:
            raise LLMProcessorError(f"サポートされていないモデルタイプです: {self.model_type}")

        return await generator(prompt)

    async def generate_response(
        self,
        query: str,
        context: List[Dict],
        timeout: int = 30
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

        prompt = self._create_prompt(query, context)

        try:
            return await asyncio.wait_for(
                self._generate_model_response(prompt),
                timeout=timeout
            )

        except asyncio.TimeoutError:
            raise LLMProcessorError("回答生成がタイムアウトしました")
        except (OpenAIAPIError, AnthropicAPIError) as e:
            raise LLMProcessorError(f"API呼び出しに失敗しました: {e}")
        except Exception as e:
            raise LLMProcessorError(f"回答生成に失敗しました: {e}") 