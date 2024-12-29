"""
Geminiモデルの実装
"""
import json
import logging
import time
from typing import Any, Dict

import google.generativeai as genai

from app.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    """Gemini LLM"""

    def __init__(self, api_key: str, model: str = 'gemini-pro', temperature: float = 0.1):
        """初期化
        
        Args:
            api_key: Google API Key
            model: モデル名
            temperature: 生成時の温度パラメータ
        """
        super().__init__(api_key=api_key, model=model, temperature=temperature)
        self._init_client()
    
    def _init_client(self) -> None:
        """クライアントの初期化"""
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={"temperature": self.temperature}
        )
    
    async def generate_text(self, prompt: str) -> str:
        """
        テキストを生成

        Args:
            prompt (str): プロンプト

        Returns:
            str: 生成されたテキスト
        """
        response = await self.client.generate_content_async(prompt)
        text = response.text
        
        # メトリクスの更新
        # Note: Gemini APIは現在トクン数を提供していないため、文字数で代用
        prompt_tokens = len(prompt)
        completion_tokens = len(text)
        # コストは現在無料のため0とする
        self.update_metrics(prompt_tokens, completion_tokens, 0.0)
        
        return text
    
    async def analyze_content(self, content: str, task: str) -> Dict[str, Any]:
        """
        コンテンツを分析

        Args:
            content (str): 分析対象のコンテンツ
            task (str): 分析タスクの種類

        Returns:
            Dict[str, Any]: 分析結果
        """
        logging.debug(f'GeminiLLM: {task}タスクの分析開始')
        start_time = time.time()

        # タスクに応じたプロンプトを生成
        prompt = self._create_analysis_prompt(task, content)
        logging.debug(f'GeminiLLM: プロンプト生成完了 ({len(prompt)}文字)')
        
        # 分析を実行
        logging.debug('GeminiLLM: API呼び出し開始')
        response = await self.client.generate_content_async(prompt)
        logging.debug('GeminiLLM: API呼び出し完了')
        
        result = self._extract_content(response.text)
        logging.debug('GeminiLLM: レスポンス解析完了')
        
        # メトリクスの更新
        prompt_tokens = len(prompt)
        completion_tokens = len(response.text)
        self.update_metrics(prompt_tokens, completion_tokens, 0.0)
        
        end_time = time.time()
        logging.debug(f'GeminiLLM: 分析完了: 処理時間 {end_time - start_time:.2f}秒')
        return result
    
    def _create_analysis_prompt(self, task: str, content: str) -> str:
        """
        分析用のプロンプトを生成

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
                '  "title": "h1.article-title",\n'
                '  "content": "div.article-content",\n'
                '  "date": "span.publish-date"\n'
                "}"
            ),
            "extract": (
                "以下のHTMLコンテンツから主要な情報を抽出してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"コンテンツ:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "title": "記事タイトル",\n'
                '  "content": "本文の要約",\n'
                '  "date": "2024-01-01"\n'
                "}"
            ),
            "error": (
                "以下のエラー情報を分析し、原因と対策を提案してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"エラー情報:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "cause": "エラーの原因",\n'
                '  "solution": "提案される対策",\n'
                '  "retry": true/false\n'
                "}"
            )
        }
        
        return prompts.get(task, f"以下の内容を分析してください:\n{content}")
    
    def _extract_content(self, text: str) -> Dict[str, Any]:
        """
        レスポンステキストからJSONコンテンツを抽出

        Args:
            text (str): レスポンステキスト

        Returns:
            Dict[str, Any]: 抽出されたコンテンツ
        """
        # テキストからJSON部分を抽出
        try:
            # 最初の{から最後の}までを抽出
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # JSON抽出に失敗した場合は、テキスト全体を返す
        return {"text": text.strip()} 