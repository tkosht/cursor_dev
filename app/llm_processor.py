"""
LLM処理

LLMを使用した回答生成を行うモジュール
"""

from typing import Dict, List, Optional

import google.generativeai as genai
import ollama
from anthropic import Anthropic
from openai import OpenAI


class LLMProcessor:
    """LLM処理クラス"""

    def __init__(self, model_type: str = "gemini", api_key: Optional[str] = None):
        """
        LLMProcessorの初期化

        Args:
            model_type: 使用するLLMの種類（デフォルト: gemini）
            api_key: API Key（必要な場合）
        """
        self.model_type = model_type
        self.api_key = api_key
        self._setup_model()

    def _setup_model(self) -> None:
        """モデルのセットアップ"""
        if self.model_type == "gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif self.model_type == "gpt":
            self.client = OpenAI(api_key=self.api_key)
        elif self.model_type == "claude":
            self.client = Anthropic(api_key=self.api_key)
        elif self.model_type == "ollama":
            self.client = ollama
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    async def generate_response(self, query: str, context: List[Dict]) -> str:
        """
        クエリと文脈から回答を生成する

        Args:
            query: ユーザーからのクエリ
            context: 関連するブックマークのリスト

        Returns:
            str: 生成された回答
        """
        # コンテキストの準備
        context_text = "\n\n".join([
            f"Tweet: {bookmark['text']}\nURL: {bookmark.get('url', 'N/A')}"
            for bookmark in context
        ])

        prompt = f"""以下のブックマークされたツイートを参考に、質問に答えてください。

コンテキスト:
{context_text}

質問: {query}

回答:"""

        if self.model_type == "gemini":
            response = await self.model.generate_content_async(prompt)
            return response.text
        elif self.model_type == "gpt":
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        elif self.model_type == "claude":
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        elif self.model_type == "ollama":
            response = await self.client.chat(
                model="mistral",
                messages=[
                    {"role": "system", "content": "ブックマークされたツイートの情報を元に、ユーザーの質問に答えてください。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}") 