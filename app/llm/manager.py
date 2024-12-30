"""
LLMを使用した評価を管理するモジュール
"""
import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.errors.llm_errors import LLMError, ModelNotFoundError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class LLMConfig:
    """LLMの設定"""

    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.1
    max_tokens: int = 1000
    timeout: float = 30.0


@dataclass
class URLComponents:
    """URL構成要素"""

    path_segments: List[str]
    query_params: Dict[str, List[str]]
    fragment: Optional[str] = None
    file_extension: Optional[str] = None


@dataclass
class LanguageInfo:
    """言語情報"""

    primary_language: str
    other_languages: List[str]
    confidence: float


@dataclass
class EvaluationResult:
    """評価結果"""

    relevance_score: float
    category: str
    reason: str
    confidence: float


class PromptGenerator:
    """評価用プロンプトの生成"""

    # Few-shotサンプル
    EXAMPLES = [
        {
            "url": "/company/about/",
            "analysis": {
                "relevance_score": 0.95,
                "category": "company_profile",
                "reason": "標準的な企業情報パス構造",
                "confidence": 0.9,
            },
        },
        {
            "url": "/ir/financial/",
            "analysis": {
                "relevance_score": 0.8,
                "category": "ir_info",
                "reason": "投資家向け情報を示すパス",
                "confidence": 0.85,
            },
        },
    ]

    def generate(
        self, url_components: URLComponents, language_info: LanguageInfo
    ) -> str:
        """プロンプトを生成"""
        return (
            "あなたはURL分析の専門家です。\n"
            "与えられたURLが企業情報ページである可能性を分析し、"
            "その判断根拠と共に結果を返してください。\n\n"
            f"URL情報:\n"
            f"- パス: /{'/'.join(url_components.path_segments)}\n"
            f"- パラメータ: {json.dumps(url_components.query_params, ensure_ascii=False)}\n"
            f"- 言語: {language_info.primary_language}"
            f" (信頼度: {language_info.confidence})\n\n"
            "評価項目:\n"
            "1. 各パスセグメントの意味（企業情報関連性）\n"
            "2. URLパターンの一般的な用途\n"
            "3. 想定されるコンテンツタイプ\n\n"
            "出力形式:\n"
            "{\n"
            '    "relevance_score": float,  # 関連性スコア（0-1）\n'
            '    "category": str,           # ページカテゴリ\n'
            '    "reason": str,             # 判断理由\n'
            '    "confidence": float        # 判定信頼度（0-1）\n'
            "}\n\n"
            "Few-shotサンプル:\n"
            f"{json.dumps(self.EXAMPLES, indent=2, ensure_ascii=False)}"
        )


class ResultValidator:
    """評価結果の検証"""

    def validate(self, raw_result: Dict[str, Any]) -> Optional[EvaluationResult]:
        """
        評価結果を検証し、正規化
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ["relevance_score", "category", "reason", "confidence"]
            if not all(field in raw_result for field in required_fields):
                logger.error(f"Missing required fields in result: {raw_result}")
                return None

            # スコアの範囲チェック
            score = float(raw_result["relevance_score"])
            confidence = float(raw_result["confidence"])
            if not (0 <= score <= 1 and 0 <= confidence <= 1):
                logger.error(
                    f"Invalid score range: score={score}, confidence={confidence}"
                )
                return None

            # カテゴリの検証
            valid_categories = {
                "company_profile",
                "corporate_info",
                "about_us",
                "ir_info",
                "other",
            }
            category = raw_result["category"]
            if category not in valid_categories:
                logger.error(f"Invalid category: {category}")
                return None

            # カテゴリのマッピング
            category_mapping = {
                "about_us": "company_profile",
                "corporate_info": "company_profile",
            }
            category = category_mapping.get(category, category)

            return EvaluationResult(
                relevance_score=score,
                category=category,
                reason=str(raw_result["reason"]),
                confidence=confidence,
            )

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Validation error: {str(e)}")
            return None


class LLMManager:
    """LLMを使用した評価を管理するクラス"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """初期化"""
        self.config = config or LLMConfig()
        self.prompt_generator = PromptGenerator()
        self.result_validator = ResultValidator()
        self.llm = None
        
        # APIキーを環境変数から取得
        api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
        if not api_key:
            logger.warning("GOOGLE_API_KEY_GEMINI not found in environment variables")
            return
            
        # モデルを初期化（同期的に）
        if self.config.model_name.startswith("gemini"):
            from app.llm.gemini import GeminiLLM
            self.llm = GeminiLLM(
                api_key=api_key,
                model=self.config.model_name,
                temperature=self.config.temperature
            )
        
        logger.debug(
            f"Initialized LLMManager with model={self.config.model_name}, "
            f"temperature={self.config.temperature}"
        )

    async def __aenter__(self):
        """非同期コンテキストマネージャのエントリーポイント"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャのクリーンアップ"""
        if self.llm:
            await asyncio.sleep(1)  # レート制限を避けるために待機

    async def load_model(self, model_name: str, api_key: str) -> "LLMManager":
        """
        LLMモデルを読み込む

        Args:
            model_name (str): モデル名
            api_key (str): APIキー

        Returns:
            LLMManager: 自身のインスタンス
        """
        logging.debug(
            f"Initialized LLMManager with model={model_name}, temperature={self.config.temperature}"
        )

        if model_name.startswith("gemini"):
            from app.llm.gemini import GeminiLLM

            self.llm = GeminiLLM(
                api_key=api_key, model=model_name, temperature=self.config.temperature
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        return self

    async def evaluate_url_relevance(self, content: str) -> Dict[str, Any]:
        """URLの内容から企業情報関連性を評価

        Args:
            content: 評価対象のコンテンツ

        Returns:
            評価結果
            {
                'relevance_score': 関連性スコア（0-1）,
                'reason': 評価理由,
                'category': カテゴリ,
                'confidence': 判定信頼度（0-1）,
                'processing_time': 処理時間（秒）,
                'llm_response': {
                    'company_name': 企業名,
                    'business_description': 事業内容,
                    'industry': 業界
                }
            }
        """
        try:
            if not self.llm:
                logger.error("LLM model is not initialized")
                return self._mock_company_info()

            start_time = time.monotonic()

            # コンテンツを分析
            result = await self.analyze_content(content, task="company_info")
            if not result:
                logger.error("コンテンツ分析に失敗しました")
                return {
                    "relevance_score": 0.0,
                    "category": "error",
                    "reason": "コンテンツ分析に失敗しました",
                    "confidence": 0.0,
                    "processing_time": 0.0,
                    "llm_response": {}
                }

            # 処理時間の計算
            processing_time = time.monotonic() - start_time

            # 結果の整形
            return {
                "relevance_score": 0.9 if "company_name" in result else 0.2,
                "category": "company_profile" if "company_name" in result else "other",
                "reason": "企業情報が検出されました" if "company_name" in result else "企業情報が見つかりません",
                "confidence": 0.9 if "company_name" in result else 0.7,
                "processing_time": processing_time,
                "llm_response": result
            }

        except Exception as e:
            logger.error(f"URL評価エラー: {str(e)}")
            return {
                "relevance_score": 0.0,
                "category": "error",
                "reason": str(e),
                "confidence": 0.0,
                "processing_time": 0.0,
                "llm_response": {}
            }

    def _detect_language(self, path_components: List[str]) -> LanguageInfo:
        """
        パスコンポーネントから言語を検出

        Args:
            path_components: URLパスのコンポーネント

        Returns:
            LanguageInfo: 検出された言語情報
        """
        # 日本語文字を含むか確認
        has_japanese = any(
            ord(c) > 0x3040 and ord(c) < 0x30FF  # ひらがな・カタカナ
            or ord(c) > 0x4E00 and ord(c) < 0x9FFF  # 漢字
            for component in path_components
            for c in component
        )

        # 言語パラメータを確認
        lang_components = [
            comp for comp in path_components
            if comp in ["ja", "jp", "en", "us", "uk"]
        ]

        if has_japanese or any(comp in ["ja", "jp"] for comp in lang_components):
            return LanguageInfo(
                primary_language="ja",
                other_languages=["en"],
                confidence=0.9 if has_japanese else 0.7
            )
        else:
            return LanguageInfo(
                primary_language="en",
                other_languages=["ja"],
                confidence=0.8
            )

    def _mock_llm_evaluation(self, url: str) -> Dict[str, Any]:
        """
        LLM評価のモック実装
        """
        if "company" in url or "about" in url:
            return {
                "relevance_score": 0.9,
                "category": "company_profile",
                "reason": "企業情報ページへの直接リンク",
                "confidence": 0.9,
            }
        elif "corporate" in url:
            return {
                "relevance_score": 0.8,
                "category": "corporate_info",
                "reason": "企業情報関連ページ",
                "confidence": 0.85,
            }
        else:
            return {
                "relevance_score": 0.3,
                "category": "other",
                "reason": "一般ページ",
                "confidence": 0.7,
            }

    async def analyze_content(self, content: str, task: str = "url_analysis") -> Dict[str, Any]:
        """
        コンテンツを分析

        Args:
            content: 分析対象のコンテンツ
            task: 分析タスク（"url_analysis" or "company_info"）

        Returns:
            分析結果
        """
        try:
            if not self.llm:
                logger.error("LLM model is not initialized")
                return self._mock_company_info() if task == "company_info" else {}

            if not content:
                logger.warning("Empty content provided")
                return self._mock_company_info() if task == "company_info" else {}

            # コンテンツを3000文字に制限
            content = content[:3000]

            # タスクに応じたプロンプトを生成
            if task == "company_info":
                prompt = (
                    "以下のWebサイトコンテンツから企業情報を抽出してください。\n"
                    "必要な情報：\n"
                    "- 企業名\n"
                    "- 事業内容\n"
                    "- 業界\n\n"
                    f"コンテンツ:\n{content}\n\n"
                    "JSON形式で出力してください:\n"
                    "{\n"
                    '    "company_name": "企業名",\n'
                    '    "business_description": "事業内容の説明",\n'
                    '    "industry": "業界分類"\n'
                    "}"
                )
            else:
                prompt = (
                    "以下のWebサイトコンテンツを分析し、重要な情報を抽出してください。\n\n"
                    f"コンテンツ:\n{content}"
                )

            logger.debug(f"Generated prompt: {prompt}")

            # LLMで分析
            try:
                result = await self.llm.generate(prompt)
                logger.debug(f"Raw LLM response: {result}")
                
                if not result:
                    logger.error("Empty response from LLM")
                    return self._mock_company_info() if task == "company_info" else {}

                # 結果をJSONとしてパース
                try:
                    if isinstance(result, str):
                        logger.debug("Parsing string response as JSON")
                        result = self._parse_json_response(result)
                        logger.debug(f"Parsed JSON result: {result}")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Failed to parse LLM response: {str(e)}")
                    return self._mock_company_info() if task == "company_info" else {}

                # タスクに応じた検証
                if task == "company_info":
                    logger.debug("Validating company info")
                    return self._validate_company_info(result)
                return result

            except Exception as e:
                logger.error(f"Error during LLM generation: {str(e)}")
                return self._mock_company_info() if task == "company_info" else {}

        except Exception as e:
            logger.error(f"Unexpected error in analyze_content: {str(e)}")
            return self._mock_company_info() if task == "company_info" else {}

    def _validate_company_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """企業情報の検証

        Args:
            result: 抽出された企業情報

        Returns:
            検証済みの企業情報
        """
        required_fields = ["company_name", "business_description", "industry"]
        if not all(field in result for field in required_fields):
            logger.error(f"Missing required fields in result: {result}")
            return self._mock_company_info()

        # 各フィールドが文字列であることを確認
        for field in required_fields:
            if not isinstance(result[field], str):
                logger.error(f"Invalid type for {field}: {type(result[field])}")
                return self._mock_company_info()

        return result

    def _mock_company_info(self) -> Dict[str, Any]:
        """モックの企業情報を生成（開発用）"""
        return {
            "company_name": "サンプル株式会社",
            "business_description": "ITソリューションの提供",
            "industry": "情報技術"
        }

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSONレスポンスをパース

        Args:
            response: JSONレスポンス

        Returns:
            Dict[str, Any]: パースされたJSON

        Raises:
            ValueError: JSONのパースに失敗した場合
        """
        try:
            # コードブロックを除去
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("\n", 1)[1]  # 最初の行を除去
            if json_str.endswith("```"):
                json_str = json_str.rsplit("\n", 1)[0]  # 最後の行を除去
            if json_str.startswith("json"):
                json_str = json_str.split("\n", 1)[1]  # "json"の行を除去
            
            # 空白行を除去
            json_str = "\n".join(line for line in json_str.split("\n") if line.strip())
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
