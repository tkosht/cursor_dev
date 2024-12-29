"""
LLMを使用した評価を管理するモジュール
"""
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class LLMConfig:
    """LLMの設定"""
    model_name: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 500
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
                "confidence": 0.9
            }
        },
        {
            "url": "/ir/financial/",
            "analysis": {
                "relevance_score": 0.8,
                "category": "ir_info",
                "reason": "投資家向け情報を示すパス",
                "confidence": 0.85
            }
        }
    ]

    def generate(
        self,
        url_components: URLComponents,
        language_info: LanguageInfo
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
            required_fields = [
                "relevance_score",
                "category",
                "reason",
                "confidence"
            ]
            if not all(field in raw_result for field in required_fields):
                logger.error(f"Missing required fields in result: {raw_result}")
                return None

            # スコアの範囲チェック
            score = float(raw_result["relevance_score"])
            confidence = float(raw_result["confidence"])
            if not (0 <= score <= 1 and 0 <= confidence <= 1):
                logger.error(f"Invalid score range: score={score}, confidence={confidence}")
                return None

            # カテゴリの検証
            valid_categories = {
                "company_profile",
                "corporate_info",
                "about_us",
                "ir_info",
                "other"
            }
            category = raw_result["category"]
            if category not in valid_categories:
                logger.error(f"Invalid category: {category}")
                return None

            return EvaluationResult(
                relevance_score=score,
                category=category,
                reason=str(raw_result["reason"]),
                confidence=confidence
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
        logger.debug(
            f"Initialized LLMManager with model={self.config.model_name}, "
            f"temperature={self.config.temperature}"
        )

    async def evaluate_url_relevance(
        self,
        url: str,
        path_components: List[str],
        query_params: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        URLの企業情報関連性を評価

        Args:
            url: 評価対象のURL
            path_components: URLパスのコンポーネント
            query_params: クエリパラメータ

        Returns:
            評価結果
            {
                'relevance_score': 関連性スコア（0-1）,
                'reason': 評価理由,
                'category': カテゴリ,
                'confidence': 判定信頼度（0-1）
            }
        """
        try:
            start_time = time.monotonic()

            # URL構成要素の作成
            url_components = URLComponents(
                path_segments=path_components,
                query_params=query_params
            )

            # 言語情報の検出（現在は簡易実装）
            language_info = self._detect_language(path_components)

            # プロンプト生成
            prompt = self.prompt_generator.generate(
                url_components,
                language_info
            )

            # LLM評価実行
            # TODO: 実際のLLM呼び出しを実装
            # 現在はモック実装
            raw_result = self._mock_llm_evaluation(url)

            # 結果の検証
            result = self.result_validator.validate(raw_result)
            if not result:
                return None

            # 処理時間の記録
            processing_time = time.monotonic() - start_time
            logger.debug(
                f"URL evaluation completed in {processing_time:.2f}s: "
                f"score={result.relevance_score:.2f}, "
                f"confidence={result.confidence:.2f}"
            )

            return {
                "relevance_score": result.relevance_score,
                "category": result.category,
                "reason": result.reason,
                "confidence": result.confidence
            }

        except Exception as e:
            logger.error(f"Error evaluating URL relevance: {str(e)}", exc_info=True)
            return None

    def _detect_language(self, path_components: List[str]) -> LanguageInfo:
        """
        言語情報を検出（簡易実装）
        """
        # パスから言語コードを検出
        lang_codes = {"ja", "en", "zh", "ko"}
        detected_lang = "ja"  # デフォルト
        confidence = 0.8

        for segment in path_components:
            if segment in lang_codes:
                detected_lang = segment
                confidence = 0.9
                break

        return LanguageInfo(
            primary_language=detected_lang,
            other_languages=[],
            confidence=confidence
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
                "confidence": 0.9
            }
        elif "corporate" in url:
            return {
                "relevance_score": 0.8,
                "category": "corporate_info",
                "reason": "企業情報関連ページ",
                "confidence": 0.85
            }
        else:
            return {
                "relevance_score": 0.3,
                "category": "other",
                "reason": "一般ページ",
                "confidence": 0.7
            } 