"""Gemini APIを使用してコンテンツを解析するモジュール。"""

import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai

logger = logging.getLogger(__name__)

# .env.testファイルを読み込む
load_dotenv('.env.test')


class GeminiAnalyzer:
    """Gemini APIを使用してコンテンツを解析するクラス。"""

    def __init__(self, api_key: str = None):
        """
        GeminiAnalyzerを初期化する。

        Args:
            api_key (str, optional): Gemini APIのキー。指定されない場合は環境変数から取得。

        Raises:
            ValueError: APIキーが指定されておらず、環境変数にも設定されていない場合
        """
        if api_key == "":
            raise ValueError("APIキーが指定されておらず、環境変数 GOOGLE_API_KEY_GEMINI も設定されていません")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY_GEMINI")
        if not self.api_key:
            raise ValueError("APIキーが指定されておらず、環境変数 GOOGLE_API_KEY_GEMINI も設定されていません")
        
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def analyze_content(self, content: dict) -> dict:
        """
        コンテンツを解析し、市場影響度やトレンドを抽出する。

        Args:
            content (dict): 解析対象のコンテンツ（title, content, urlを含む）

        Returns:
            dict: 解析結果を含む辞書

        Raises:
            ValueError: コンテンツが不正な形式の場合
        """
        if not isinstance(content, dict) or not all(k in content for k in ['title', 'content', 'url']):
            raise ValueError("Invalid content format")

        prompt = self._construct_prompt(content)
        response = self._call_gemini_api(prompt)
        return self._parse_response(response)

    def _construct_prompt(self, content: dict) -> str:
        """
        Gemini APIに送信するプロンプトを生成する。

        Args:
            content (dict): 解析対象のコンテンツ

        Returns:
            str: 生成されたプロンプト
        """
        current_time = datetime.now().isoformat()
        return f"""
        以下のコンテンツを解析し、市場影響度とトレンドを抽出してください。
        広告や不要な情報は除外し、以下の形式でJSON形式で返してください：

        {{
            "market_impact": 0.0-1.0の数値,
            "trends": ["トレンド1", "トレンド2", ...],
            "entities": [
                {{"name": "企業名や製品名", "type": "COMPANY/PRODUCT/SERVICE", "description": "説明"}}
            ],
            "relationships": [
                {{"source": "エンティティ1", "target": "エンティティ2", "type": "INFLUENCES/COMPETES/DEVELOPS",
                  "strength": 0.0-1.0}}
            ]
        }}

        タイトル: {content.get('title', 'Unknown')}
        URL: {content.get('url', 'Unknown')}
        日時: {current_time}

        コンテンツ:
        {content.get('content', '')}
        """

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Gemini APIを呼び出し、レスポンスを取得する。

        Args:
            prompt (str): APIに送信するプロンプト

        Returns:
            str: APIからのレスポンス

        Raises:
            ConnectionError: API呼び出しに失敗した場合
        """
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise ConnectionError(f"Gemini APIの呼び出しに失敗しました: {str(e)}")

    def _parse_response(self, response: str) -> dict:
        """
        APIレスポンスをパースし、構造化されたデータに変換する。

        Args:
            response (str): APIからのレスポンス

        Returns:
            dict: パースされた解析結果

        Raises:
            ValueError: レスポンスのパースに失敗した場合
        """
        if not response:
            raise ValueError("Invalid JSON format")

        try:
            # マークダウンのコードブロックを処理
            if "```json" in response:
                json_content = response.split("```json")[1].split("```")[0].strip()
            else:
                json_content = response.strip()

            result = json.loads(json_content)
            return self._validate_json_result(result)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    def _validate_json_result(self, result: dict) -> dict:
        """
        JSONの内容を検証する。

        Args:
            result (dict): 検証対象のJSON

        Returns:
            dict: 検証済みのJSON

        Raises:
            ValueError: 検証に失敗した場合
        """
        # 必須フィールドの検証
        required_fields = ["market_impact", "trends", "entities", "relationships"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"必須フィールド {field} が見つかりません")

        # market_impactの範囲チェック
        if not 0 <= result["market_impact"] <= 1:
            raise ValueError("Impact score must be between 0 and 1")

        return result 