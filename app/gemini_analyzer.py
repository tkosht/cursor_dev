"""Gemini APIを使用してコンテンツを解析するモジュール。"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai
from google.generativeai import GenerativeModel

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini APIを使用してコンテンツを解析するクラス。"""

    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """
        Args:
            api_key (str): Gemini APIのAPIキー
            model_name (str, optional): 使用するモデル名. デフォルトは "gemini-pro"

        Raises:
            ValueError: APIキーが指定されていない場合
        """
        if not api_key:
            raise ValueError("API key is required")

        genai.configure(api_key=api_key)
        self._model = GenerativeModel(model_name)

    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツを分析し、市場への影響を評価

        Args:
            content (Dict[str, Any]): 分析対象のコンテンツ
                {
                    'title': str,  # コンテンツのタイトル
                    'content': str,  # 本文
                    'date': Optional[datetime],  # 公開日時
                    'url': str  # コンテンツのURL
                }

        Returns:
            Dict[str, Any]: 分析結果
                {
                    'entities': List[Dict],  # 抽出されたエンティティ情報
                    'relationships': List[Dict],  # エンティティ間の関係性
                    'impact_scores': Dict[str, float],  # 各エンティティの市場影響度
                    'summary': str  # 分析の要約
                }

        Raises:
            ValueError: コンテンツの形式が不正な場合
            RuntimeError: API呼び出しに失敗した場合
        """
        if not self._validate_content(content):
            raise ValueError("Invalid content format")

        try:
            prompt = self._construct_prompt(content)
            response = self._call_gemini_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(f"Failed to analyze content: {str(e)}")

    def _validate_content(self, content: Dict[str, Any]) -> bool:
        """コンテンツの形式を検証

        Args:
            content (Dict[str, Any]): 検証対象のコンテンツ

        Returns:
            bool: 検証結果（True: 正常、False: 不正）
        """
        required_keys = {'title', 'content', 'url'}
        return all(key in content for key in required_keys)

    def _construct_prompt(self, content: Dict[str, Any]) -> str:
        """分析用のプロンプトを生成

        Args:
            content (Dict[str, Any]): プロンプト生成に使用するコンテンツ

        Returns:
            str: 生成されたプロンプト
        """
        date_str = content['date'].isoformat() if content.get('date') else 'Unknown'
        return f"""以下のコンテンツを分析し、市場への影響を評価してください。

タイトル: {content['title']}
URL: {content['url']}
公開日時: {date_str}

本文:
{content['content']}

以下の形式でJSON形式で回答してください:
{{
    "entities": [
        {{
            "id": "一意のID",
            "type": "Company/Product/Technology/Market",
            "name": "エンティティ名",
            "description": "説明"
        }}
    ],
    "relationships": [
        {{
            "source_id": "関係の起点となるエンティティID",
            "target_id": "関係の終点となるエンティティID",
            "type": "関係の種類（PRODUCES/COMPETES/USES等）",
            "strength": 0.0-1.0の数値,
            "description": "関係の説明"
        }}
    ],
    "impact_scores": {{
        "エンティティID": 0.0-1.0の数値
    }},
    "summary": "分析の要約（日本語）"
}}"""

    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Gemini APIを呼び出し

        Args:
            prompt (str): 送信するプロンプト

        Returns:
            Dict[str, Any]: APIからのレスポンス

        Raises:
            RuntimeError: API呼び出しに失敗した場合
        """
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """APIレスポンスをパース

        Args:
            response (str): パース対象のレスポンス

        Returns:
            Dict[str, Any]: パース結果

        Raises:
            ValueError: レスポンスの形式が不正な場合
        """
        try:
            import json
            result = json.loads(response)

            # 必須キーの存在確認
            required_keys = {'entities', 'relationships', 'impact_scores', 'summary'}
            if not all(key in result for key in required_keys):
                raise ValueError("Missing required keys in response")

            # スコアの範囲チェック
            for score in result['impact_scores'].values():
                if not 0 <= score <= 1:
                    raise ValueError("Impact score must be between 0 and 1")

            return result
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in response")
        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}") 