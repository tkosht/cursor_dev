"""
LLMを使用した評価を管理するモジュール
"""
import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from app.llm.base import BaseLLM

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
        self.llm: Optional[BaseLLM] = None

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
                temperature=self.config.temperature,
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
                    "llm_response": {},
                }

            # 処理時間の計算
            processing_time = time.monotonic() - start_time

            # 結果の整形
            return {
                "relevance_score": 0.9 if "company_name" in result else 0.2,
                "category": "company_profile" if "company_name" in result else "other",
                "reason": "企業情報が検出されました"
                if "company_name" in result
                else "企業情報が見つかりません",
                "confidence": 0.9 if "company_name" in result else 0.7,
                "processing_time": processing_time,
                "llm_response": result,
            }

        except Exception as e:
            logger.error(f"URL評価エラー: {str(e)}")
            return {
                "relevance_score": 0.0,
                "category": "error",
                "reason": str(e),
                "confidence": 0.0,
                "processing_time": 0.0,
                "llm_response": {},
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
            ord(c) > 0x3040
            and ord(c) < 0x30FF  # ひらがな・カタカナ
            or ord(c) > 0x4E00
            and ord(c) < 0x9FFF  # 漢字
            for component in path_components
            for c in component
        )

        # 言語パラメータを確認
        lang_components = [
            comp for comp in path_components if comp in ["ja", "jp", "en", "us", "uk"]
        ]

        if has_japanese or any(comp in ["ja", "jp"] for comp in lang_components):
            return LanguageInfo(
                primary_language="ja",
                other_languages=["en"],
                confidence=0.9 if has_japanese else 0.7,
            )
        else:
            return LanguageInfo(
                primary_language="en", other_languages=["ja"], confidence=0.8
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

    async def analyze_content(
        self,
        content: str,
        task: str = "url_analysis"
    ) -> Dict[str, Any]:
        """コンテンツを分析する

        Args:
            content: 分析対象のコンテンツ
            task: 分析タスクの種類（デフォルト: "url_analysis"）

        Returns:
            Dict[str, Any]: 分析結果
        """
        try:
            if not self._validate_input(content):
                return self._get_default_response(task)

            # コンテンツを3000文字に制限
            content = content[:3000]
            
            # タスクに応じた処理を実行
            if task == "company_info":
                return await self._analyze_company_info(content)
            return await self._analyze_general_content(content)

        except Exception as e:
            logger.error(f"Unexpected error in analyze_content: {str(e)}")
            return self._get_default_response(task)

    def _validate_input(self, content: str) -> bool:
        """入力の妥当性を検証

        Args:
            content: 検証対象のコンテンツ

        Returns:
            bool: 入力が有効な場合はTrue
        """
        if not self.llm:
            logger.error("LLM model is not initialized")
            return False

        if not content:
            logger.warning("Empty content provided")
            return False

        return True

    def _get_default_response(self, task: str) -> Dict[str, Any]:
        """デフォルトのレスポンスを取得

        Args:
            task: タスクの種類

        Returns:
            Dict[str, Any]: デフォルトのレスポンス
        """
        if task == "company_info":
            return self._mock_company_info()
        return {}

    async def _analyze_company_info(self, content: str) -> Dict[str, Any]:
        """企業情報を分析

        Args:
            content: 分析対象のコンテンツ

        Returns:
            Dict[str, Any]: 分析結果
        """
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

        result = await self._execute_llm_analysis(prompt)
        if not result:
            return self._mock_company_info()

        return self._validate_company_info(result)

    async def _analyze_general_content(self, content: str) -> Dict[str, Any]:
        """一般的なコンテンツを分析

        Args:
            content: 分析対象のコンテンツ

        Returns:
            Dict[str, Any]: 分析結果
        """
        prompt = (
            "以下のWebサイトコンテンツを分析し、重要な情報を抽出してください。\n\n"
            f"コンテンツ:\n{content}"
        )

        return await self._execute_llm_analysis(prompt)

    async def _execute_llm_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """LLMによる分析を実行

        Args:
            prompt: 分析用プロンプト

        Returns:
            Optional[Dict[str, Any]]: 分析結果
        """
        try:
            logger.debug(f"Generated prompt: {prompt}")
            result = await self.llm.generate(prompt)
            logger.debug(f"Raw LLM response: {result}")

            if not result:
                logger.error("Empty response from LLM")
                return None

            if isinstance(result, str):
                logger.debug("Parsing string response as JSON")
                result = self._parse_json_response(result)
                logger.debug(f"Parsed JSON result: {result}")

            return result

        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            return None

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
            "industry": "情報技術",
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
            # JSONブロックを抽出
            json_block_match = re.search(r'```json\s*\n(.*?)\n\s*```', response, re.DOTALL)
            if not json_block_match:
                raise ValueError("No JSON block found in response")
            
            json_str = json_block_match.group(1).strip()
            
            # 空白行を除去
            json_str = "\n".join(line for line in json_str.split("\n") if line.strip())
            
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            raise ValueError(f"Invalid JSON response: {str(e)}")

    async def generate_selectors(
        self,
        soup: "BeautifulSoup",
        target_data: Dict[str, str]
    ) -> Dict[str, str]:
        """HTMLからデータ抽出用のセレクタを生成

        Args:
            soup: BeautifulSoupオブジェクト
            target_data: 取得対象データの辞書

        Returns:
            キーとセレクタのマッピング辞書
        """
        if not self.llm:
            raise ValueError("LLMが初期化されていません")

        # プロンプトを生成
        prompt = self._generate_selector_prompt(soup, target_data)

        try:
            # LLMで解析
            response = await self.llm.generate(prompt)
            selectors = self._parse_json_response(response)

            # セレクタを検証
            return await self._validate_selectors(soup, selectors, target_data)

        except Exception as e:
            logger.error(f"セレクタ生成エラー: {str(e)}")
            raise

    def _generate_selector_prompt(
        self,
        soup: "BeautifulSoup",
        target_data: Dict[str, str]
    ) -> str:
        """セレクタ生成用のプロンプトを生成

        Args:
            soup: BeautifulSoupオブジェクト
            target_data: 取得対象データの辞書

        Returns:
            str: 生成されたプロンプト
        """
        # HTML構造を分析
        html_structure = self._analyze_html_structure(soup)

        # プロンプトを生成
        prompt = (
            "あなたはHTML解析の専門家です。以下のHTML構造から、指定された財務データを抽出するための"
            "最適なCSSセレクタを生成してください。\n\n"
            f"HTML構造:\n{html_structure}\n\n"
            "抽出対象データ:\n"
        )
        for key, label in target_data.items():
            prompt += f"- {key}: {label}\n"

        prompt += (
            "\n以下の形式で、JSONのみを出力してください。説明は不要です：\n"
            "```json\n"
            "{\n"
            '    "データキー": "CSSセレクタ"\n'
            "}\n"
            "```\n\n"
            "セレクタ生成の注意事項:\n"
            "1. セレクタは可能な限り具体的に指定\n"
            "2. class名やid属性を優先的に使用\n"
            "3. 数値を含むテキストを優先的に抽出\n"
            "4. 複数の候補がある場合は最も信頼性の高いものを選択"
        )

        return prompt

    async def _validate_selectors(
        self,
        soup: "BeautifulSoup",
        selectors: Dict[str, str],
        target_data: Dict[str, str]
    ) -> Dict[str, str]:
        """セレクタの有効性を検証

        Args:
            soup: BeautifulSoupオブジェクト
            selectors: 検証対象のセレクタ辞書
            target_data: 取得対象データの辞書

        Returns:
            Dict[str, str]: 検証済みのセレクタ辞書
        """
        validated_selectors = {}

        for key, selector in selectors.items():
            if key not in target_data:
                continue

            # セレクタの有効性を確認
            elements = soup.select(selector)
            if not elements:
                logger.warning(f"セレクタ {selector} で要素が見つかりません")
                continue

            # 抽出されたテキストが目的のデータらしいかチェック
            text = elements[0].get_text(strip=True)
            if not self._validate_extracted_text(text, target_data[key]):
                logger.warning(f"抽出されたテキスト '{text}' が期待と異なります")
                continue

            validated_selectors[key] = selector

        if not validated_selectors:
            raise ValueError("有効なセレクタが生成できませんでした")

        return validated_selectors

    def _validate_extracted_text(self, text: str, expected_label: str) -> bool:
        """抽出されたテキストの妥当性を検証

        Args:
            text: 抽出されたテキスト
            expected_label: 期待されるラベル

        Returns:
            bool: テキストが妥当な場合はTrue
        """
        # 数値を含むかチェック
        has_number = any(char.isdigit() for char in text)
        
        # 円マークを含むかチェック
        has_yen = "円" in text
        
        # ラベルとの関連性をチェック
        label_similarity = self._calculate_text_similarity(text, expected_label)
        
        return has_number and has_yen and label_similarity > 0.5

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算

        Args:
            text1: 1つ目のテキスト
            text2: 2つ目のテキスト

        Returns:
            float: 類似度（0-1）
        """
        # 簡易的な類似度計算（実際の実装ではより高度なアルゴリズムを使用）
        common_chars = set(text1) & set(text2)
        total_chars = set(text1) | set(text2)
        return len(common_chars) / len(total_chars) if total_chars else 0.0

    def _analyze_html_structure(self, soup: "BeautifulSoup") -> str:
        """HTML構造を分析し、要約を生成

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            HTML構造の要約
        """
        try:
            structure_parts = []

            # タイトルの分析
            title_info = self._analyze_title(soup)
            if title_info:
                structure_parts.append(title_info)

            # 見出しの分析
            heading_info = self._analyze_headings(soup)
            if heading_info:
                structure_parts.append(heading_info)

            # メインコンテンツの分析
            content_info = self._analyze_main_content(soup)
            if content_info:
                structure_parts.extend(content_info)

            # データ属性の分析
            data_info = self._analyze_data_attributes(soup)
            if data_info:
                structure_parts.append(data_info)

            return "\n".join(structure_parts) if structure_parts else "HTML構造を特定できません"

        except Exception as e:
            logger.error(f"HTML構造分析エラー: {str(e)}")
            return "HTML構造の分析に失敗しました"

    def _analyze_title(self, soup: "BeautifulSoup") -> Optional[str]:
        """タイトル要素を分析

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: タイトル情報
        """
        if soup.title:
            return f"title: {soup.title.string}"
        return None

    def _analyze_headings(self, soup: "BeautifulSoup") -> Optional[str]:
        """見出し要素を分析

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: 見出し情報
        """
        headings = []
        for tag in ["h1", "h2", "h3"]:
            elements = soup.find_all(tag)
            if elements:
                headings.append(f"{tag}: {len(elements)}個")
        
        if headings:
            return f"見出し: {', '.join(headings)}"
        return None

    def _analyze_main_content(self, soup: "BeautifulSoup") -> List[str]:
        """メインコンテンツを分析

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            List[str]: メインコンテンツ情報のリスト
        """
        content_info = []
        for tag in ["main", "article"]:
            elements = soup.find_all(tag)
            if elements:
                content_info.append(f"{tag}: {len(elements)}個")
        return content_info

    def _analyze_data_attributes(self, soup: "BeautifulSoup") -> Optional[str]:
        """データ属性を分析

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[str]: データ属性情報
        """
        data_elements = soup.find_all(
            lambda tag: tag.attrs and any(k.startswith("data-") for k in tag.attrs.keys())
        )
        if data_elements:
            return f"データ属性要素: {len(data_elements)}個"
        return None

    async def validate_data(
        self,
        extracted_data: Dict[str, str],
        target_data: Dict[str, str]
    ) -> bool:
        """抽出したデータを検証

        Args:
            extracted_data: 抽出したデータの辞書
            target_data: 取得対象データの辞書

        Returns:
            bool: データが有効な場合はTrue
        """
        if not self.llm:
            raise ValueError("LLMが初期化されていません")

        # 必要なキーが全て存在するか確認
        if not all(key in extracted_data for key in target_data):
            logger.warning("必要なデータが不足しています")
            return False

        # 各データの妥当性を検証
        for key, value in extracted_data.items():
            if not self._validate_financial_data(value, target_data.get(key, "")):
                logger.warning(f"データの検証に失敗: {key}={value}")
                return False

        return True

    def _validate_financial_data(self, value: str, expected_label: str) -> bool:
        """財務データの妥当性を検証

        Args:
            value: 検証対象の値
            expected_label: 期待されるラベル

        Returns:
            bool: データが有効な場合はTrue
        """
        # 空文字列や None をチェック
        if not value or not expected_label:
            return False

        # 数値を含むかチェック
        has_number = any(char.isdigit() for char in value)
        if not has_number:
            return False

        # 単位（円）を含むかチェック
        has_unit = "円" in value
        if not has_unit:
            return False

        # 数値のフォーマットをチェック
        number_part = "".join(char for char in value if char.isdigit() or char in ".,")
        try:
            float(number_part.replace(",", ""))
        except ValueError:
            return False

        # ラベルとの関連性をチェック
        label_similarity = self._calculate_text_similarity(value, expected_label)
        if label_similarity < 0.3:  # 閾値は調整可能
            return False

        return True

    async def extract_data(self, prompt: str) -> Dict[str, str]:
        """データを抽出する

        Args:
            prompt: 抽出用のプロンプト

        Returns:
            Dict[str, str]: 抽出したデータの辞書
        """
        try:
            # LLMを使用してデータを抽出
            response = await self.llm.generate(prompt)
            
            # レスポンスをパース
            data = {}
            for line in response.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip()
            
            return data
            
        except Exception as e:
            logger.error(f"データ抽出エラー: {str(e)}")
            raise
