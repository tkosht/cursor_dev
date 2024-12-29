"""
Geminiモデルの実装
"""
import asyncio
import json
import logging
from typing import Any, Dict

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
        return await super().analyze_content(content, task)

    async def _analyze_content_impl(self, content: str, task: str) -> Dict[str, Any]:
        """
        コンテンツ分析の実装

        Args:
            content (str): 分析対象のコンテンツ
            task (str): 分析タスクの種類

        Returns:
            Dict[str, Any]: 分析結果
        """
        logging.debug(f"GeminiLLM: {task}タスクの分析開始")

        # タスクに応じたプロンプトを生成
        prompt = self._create_analysis_prompt(task, content)
        logging.debug(f"GeminiLLM: プロンプト生成完了 ({len(prompt)}文字)")

        for attempt in range(self.MAX_RETRIES):
            try:
                # 分析を実行
                logging.debug("GeminiLLM: API呼び出し開始")
                response = await self.client.generate_content_async(prompt)
                logging.debug("GeminiLLM: API呼び出し完了")

                if not response or not response.text:
                    logging.error("GeminiLLM: 空のレスポンス")
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                        continue
                    return {
                        "relevance_score": 0.1,
                        "category": "other",
                        "reason": "APIレスポンスエラー",
                        "confidence": 0.1,
                    }

                result = self._extract_content(response.text)
                logging.debug("GeminiLLM: レスポンス解析完了")

                # メトリクスの更新
                prompt_tokens = len(prompt)
                completion_tokens = len(response.text)
                self.update_metrics(prompt_tokens, completion_tokens, 0.0)

                return result

            except Exception as e:
                logging.error(f"GeminiLLM: 分析エラー - {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                return {
                    "relevance_score": 0.1,
                    "category": "other",
                    "reason": f"分析エラー: {str(e)}",
                    "confidence": 0.1,
                }

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
            ),
            "url_analysis": (
                "以下のURL情報を分析し、企業情報ページとしての関連性を評価してください。\n"
                "結果はJSON形式で返してください。\n\n"
                f"URL情報:\n{content}\n\n"
                "期待する形式:\n"
                "{\n"
                '  "relevance_score": 0.95,  # 関連性スコア（0-1）\n'
                '  "category": "about_us",  # ページカテゴリ\n'
                '  "reason": "会社紹介を示すパス構造",  # 判断理由\n'
                '  "confidence": 0.9  # 判定信頼度（0-1）\n'
                "}\n\n"
                "カテゴリの判定基準（優先順位順）:\n"
                "1. about_us（会社紹介）:\n"
                "   - /about/company/, /company/about/, /about/company-index\n"
                "   - /about-us/, /about/us/を含むパス\n"
                "2. company_profile（会社概要）:\n"
                "   - /about/, /profile/を含むパス（about_usの条件に該当しない場合）\n"
                "3. corporate_info（企業情報）:\n"
                "   - /company/, /corporate/のみのパス\n"
                "4. ir_info（IR情報）:\n"
                "   - /ir/, /investor/を含むパス\n"
                "5. other（その他）:\n"
                "   - 上記以外のパス\n"
                "   - エラーや存在しないドメイン\n\n"
                "信頼度の判定基準:\n"
                "1. 高信頼度（0.9-1.0）:\n"
                "   - 明確なパスパターンと完全一致\n"
                "   - 正常なドメインでアクセス可能\n"
                "2. 中信頼度（0.5-0.8）:\n"
                "   - 一般的なパスパターンと部分一致\n"
                "   - パスの意図が不明確\n"
                "3. 低信頼度（0.0-0.4）:\n"
                "   - エラーや存在しないドメイン（必ず0.3以下）\n"
                "   - パスパターンが不適切\n\n"
                "関連性スコアの判定基準:\n"
                "1. 高関連（0.9-1.0）:\n"
                "   - 企業情報に直接関連するパス\n"
                "   - 正常なドメインでアクセス可能\n"
                "2. 中関連（0.5-0.8）:\n"
                "   - 間接的に関連するパス\n"
                "   - パスの意図が不明確\n"
                "3. 低関連（0.0-0.4）:\n"
                "   - 関連性の低いパス\n"
                "   - エラーや存在しないドメイン（必ず0.3以下）\n\n"
                "重要な注意事項:\n"
                "1. 存在しないドメインの場合:\n"
                "   - カテゴリは必ず'other'\n"
                "   - 信頼度は必ず0.3以下\n"
                "   - 関連性スコアは必ず0.3以下\n"
                "2. カテゴリ判定は優先順位に従う\n"
                "3. パスパターンは完全一致を優先"
            ),
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
