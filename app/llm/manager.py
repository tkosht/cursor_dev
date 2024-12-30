"""
LLMを使用した評価を管理するモジュール
"""
import asyncio
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

    async def evaluate_url_relevance(
        self, url: str, path_components: List[str], query_params: Dict[str, List[str]]
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
                'confidence': 判定信頼度（0-1）,
                'processing_time': 処理時間（秒）
            }
        """
        try:
            if not self.llm:
                raise ValueError("LLMモデルがロードされていません")

            start_time = time.monotonic()

            # URL構成要素の作成
            url_components = URLComponents(
                path_segments=path_components, query_params=query_params
            )

            # 言語情報の検出
            language_info = self._detect_language(path_components)

            # プロンプト生成
            prompt = self.prompt_generator.generate(url_components, language_info)

            # LLM評価実行
            raw_result = await self.llm.analyze_content(prompt, task="url_analysis")
            if not raw_result:
                logger.error("LLM評価結果が空です")
                return None

            # 結果の検証
            result = self.result_validator.validate(raw_result)
            if not result:
                logger.error("評価結果の検証に失敗しました")
                return None

            # 処理時間の計算
            processing_time = time.monotonic() - start_time

            # 結果の整形
            return {
                "relevance_score": result.relevance_score,
                "category": result.category,
                "reason": result.reason,
                "confidence": result.confidence,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"URL評価エラー: {str(e)}")
            return None

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
        """コンテンツを分析

        Args:
            content: 分析対象のテキストコンテンツ
            task: 分析タスクの種類（"url_analysis" or "company_info"）

        Returns:
            分析結果
        """
        if task == "company_info":
            prompt = (
                "あなたは企業情報抽出の専門家です。\n"
                "与えられたWebページのコンテンツから、企業の基本情報を抽出してください。\n\n"
                "抽出する情報:\n"
                "1. 企業名\n"
                "2. 事業内容\n"
                "3. 業界\n\n"
                "出力形式:\n"
                "{\n"
                '    "company_name": str,      # 企業名\n'
                '    "business_description": str,  # 事業内容の説明\n'
                '    "industry": str           # 業界\n'
                "}\n\n"
                f"コンテンツ:\n{content[:3000]}"  # コンテンツは3000文字までに制限
            )
        else:
            # 既存のURL分析用プロンプト生成ロジック
            return await self.evaluate_url_relevance(content, [], {})

        try:
            if not self.llm:
                # モックデータを返す（開発用）
                return self._mock_company_info()

            response = await self.llm.generate(prompt)
            try:
                result = json.loads(response)
                return self._validate_company_info(result)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response}")
                return self._mock_company_info()

        except Exception as e:
            logger.error(f"Error in analyze_content: {str(e)}")
            return self._mock_company_info()

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
