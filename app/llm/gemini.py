"""
Geminiモデルの実装
"""
import asyncio
import json
import logging
from typing import Any, Dict, Optional

import google.generativeai as genai

from app.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    """Gemini LLM"""

    MAX_RETRIES = 3  # 最大リトライ回数
    RETRY_DELAY = 1  # リトライ間隔（秒）

    def __init__(
        self, api_key: str, model: str = "gemini-pro", temperature: float = 0.1
    ):
        """初期化

        Args:
            api_key: Google API Key
            model: モデル名
            temperature: 生成時の温度パラメータ
        """
        super().__init__(api_key=api_key, model=model, temperature=temperature)
        self._init_client()  # クライアントを初期化

    def _init_client(self) -> None:
        """クライアントの初期化

        Raises:
            ValueError: APIキーが設定されていない場合
        """
        if not self.api_key:
            raise ValueError("APIキーが設定されていません")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model, generation_config={"temperature": self.temperature}
        )

    async def generate_text(self, prompt: str) -> str:
        """テキストを生成

        Args:
            prompt (str): プロンプト

        Returns:
            str: 生成されたテキスト

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            response = await self.client.generate_content_async(prompt)
            text = response.text if response else ""

            # メトリクスの更新
            prompt_tokens = len(prompt)
            completion_tokens = len(text)
            self.update_metrics(prompt_tokens, completion_tokens, 0.0)

            return text

        except Exception as e:
            # エラー時のメトリクス更新
            self.update_metrics(len(prompt), 0, 0.0)
            self.metrics.error_count += 1
            raise e

    async def analyze(self, prompt: str) -> Dict[str, Any]:
        """プロンプトを分析

        Args:
            prompt (str): 分析対象のプロンプト

        Returns:
            Dict[str, Any]: 分析結果
        """
        try:
            return await self._execute_analysis(prompt)
        except Exception as e:
            logging.error(f"分析エラー: {str(e)}")
            return self._create_error_response(f"分析エラー: {str(e)}")

    async def analyze_content(self, content: str, task: str) -> Dict[str, Any]:
        """コンテンツを分析

        Args:
            content (str): 分析対象のコンテンツ
            task (str): 分析タスクの種類

        Returns:
            Dict[str, Any]: 分析結果
        """
        if not content:
            return self._create_error_response("空のコンテンツが入力されました")

        try:
            prompt = self._create_analysis_prompt(task, content)
            return await self._execute_analysis(prompt)
        except Exception as e:
            logging.error(f"分析エラー: {str(e)}")
            return self._create_error_response(f"分析エラー: {str(e)}")

    async def _execute_analysis(self, prompt: str) -> Dict[str, Any]:
        """LLMを使用して分析を実行

        Args:
            prompt (str): 分析用プロンプト

        Returns:
            Dict[str, Any]: 分析結果
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self._attempt_analysis(prompt)
                if result:
                    return result

                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                return self._create_error_response("分析に失敗しました")

            except Exception as e:
                last_error = e
                logging.error(f"分析エラー（試行{attempt + 1}）: {str(e)}")
                self.metrics.error_count += 1

                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

        return self._create_error_response(f"分析エラー: {str(last_error)}")

    async def _attempt_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """1回の分析を試行

        Args:
            prompt (str): 分析用プロンプト

        Returns:
            Optional[Dict[str, Any]]: 分析結果、失敗時はNone
        """
        try:
            response = await self.client.generate_content_async(prompt)
            if not response or not response.text:
                return None

            # レスポンスからJSONを抽出
            result = self._extract_json(response.text)
            if not result:
                return None

            # メトリクスの更新
            self.update_metrics(len(prompt), len(response.text), 0.0)

            return result

        except Exception as e:
            # エラー時のメトリクス更新
            self.update_metrics(len(prompt), 0, 0.0)
            raise e

    def _create_error_response(self, reason: str) -> Dict[str, Any]:
        """エラーレスポンスを生成

        Args:
            reason (str): エラーの理由

        Returns:
            Dict[str, Any]: エラーレスポンス
        """
        return {
            "relevance_score": 0.1,
            "category": "other",
            "reason": reason,
            "confidence": 0.1,
        }

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """テキストからJSONを抽出

        Args:
            text (str): 抽出対象のテキスト

        Returns:
            Optional[Dict[str, Any]]: 抽出されたJSON、失敗時はNone
        """
        try:
            # JSONブロックを探す
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                return None

            # JSONを抽出して解析
            json_str = text[start:end + 1]
            result = json.loads(json_str)

            # 必要なフィールドの存在を確認
            required_fields = ["relevance_score", "category", "reason", "confidence"]
            if not all(field in result for field in required_fields):
                return None

            return result

        except json.JSONDecodeError:
            return None
        except Exception as e:
            logging.error(f"JSON抽出エラー: {str(e)}")
            return None

    def _create_analysis_prompt(self, task: str, content: str) -> str:
        """分析用のプロンプトを生成

        Args:
            task (str): 分析タスクの種類
            content (str): 分析対象のコンテンツ

        Returns:
            str: 生成されたプロンプト
        """
        prompts = {
            "selector": (
                "以下のHTMLコンテンツから必要な情報を抽出するためのCSSセレクタを生成してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"コンテンツ:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "relevance_score": 0.8,\n'
                '  "category": "selector",\n'
                '  "reason": "適切なセレクタを生成",\n'
                '  "confidence": 0.9\n'
                "}"
            ),
            "extract": (
                "以下のHTMLコンテンツから主要な情報を抽出してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"コンテンツ:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "relevance_score": 0.8,\n'
                '  "category": "content",\n'
                '  "reason": "主要情報を抽出",\n'
                '  "confidence": 0.9\n'
                "}"
            ),
            "error": (
                "以下のエラー情報を分析し、原因と対策を提案してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"エラー情報:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "relevance_score": 0.8,\n'
                '  "category": "error",\n'
                '  "reason": "エラーの分析結果",\n'
                '  "confidence": 0.9\n'
                "}"
            ),
            "url_analysis": (
                "以下のURLの関連性を分析してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"URL:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "relevance_score": 0.8,\n'
                '  "category": "url",\n'
                '  "reason": "URLの分析結果",\n'
                '  "confidence": 0.9\n'
                "}"
            ),
        }

        return prompts.get(
            task,
            f"以下のコンテンツを分析してください。\n{content}\n\n"
            "結果はJSON形式で返してください。"
        )
