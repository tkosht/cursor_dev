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
        self.model = self.config.model_name

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
        self.model = model_name  # modelプロパティを設定
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

    def _create_selector_prompt(self, html: str, target_data: Dict[str, str]) -> str:
        """セレクタ生成用のプロンプトを作成

        Args:
            html (str): HTML文字列
            target_data (Dict[str, str]): 抽出対象のデータ定義

        Returns:
            str: 生成されたプロンプト
        """
        soup = BeautifulSoup(html, "html.parser")
        structure = str(soup)

        return (
            "HTMLからデータを抽出するためのCSSセレクタを生成してください。\n\n"
            f"HTML構造:\n{structure}\n\n"
            "抽出対象データ:\n"
            f"{json.dumps(target_data, ensure_ascii=False, indent=2)}\n\n"
            "以下の形式でJSONを返してください:\n"
            "{\n"
            '    "データキー": "CSSセレクタ",\n'
            '    ...\n'
            "}\n"
        )

    def _create_validation_prompt(self, extracted_data: Dict[str, str], target_data: Dict[str, str]) -> str:
        """データ検証用のプロンプトを作成

        Args:
            extracted_data: 抽出したデータの辞書
            target_data: 取得対象データの辞書

        Returns:
            str: 生成されたプロンプト
        """
        prompt = (
            "あなたはデータ検証の専門家です。以下の抽出データが期待する内容と一致するか検証してください。\n\n"
            "抽出データ:\n"
        )
        for key, value in extracted_data.items():
            prompt += f"- {key}: {value}\n"

        prompt += (
            "\n期待データ:\n"
        )
        for key, label in target_data.items():
            prompt += f"- {key}: {label}\n"

        prompt += (
            "\n以下の形式で、検証結果のみを出力してください。説明は不要です：\n"
            "```json\n"
            "{\n"
            '    "is_valid": true/false\n'
            "}\n"
            "```\n\n"
            "検証の注意事項:\n"
            "1. 数値データの場合、単位（円）が正しいか確認\n"
            "2. 日付データの場合、フォーマットが正しいか確認\n"
            "3. テキストデータの場合、内容が期待と一致するか確認\n"
            "4. 不足しているデータがないか確認"
        )

        return prompt

    def _analyze_html_structure(self, soup: BeautifulSoup) -> str:
        """HTML構造を分析し、要約を生成

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            str: HTML構造の要約
        """
        structure_parts = []

        # タイトルの分析
        if soup.title:
            structure_parts.append(f"title: {soup.title.string}")

        # 見出しの分析
        headings = []
        for tag in ["h1", "h2", "h3"]:
            elements = soup.find_all(tag)
            if elements:
                headings.append(f"{tag}: {len(elements)}個")
        if headings:
            structure_parts.append(f"見出し: {', '.join(headings)}")

        # メインコンテンツの分析
        for tag in ["main", "article"]:
            elements = soup.find_all(tag)
            if elements:
                structure_parts.append(f"{tag}: {len(elements)}個")

        # データ属性の分析
        data_elements = soup.find_all(
            lambda tag: tag.attrs and any(k.startswith("data-") for k in tag.attrs.keys())
        )
        if data_elements:
            structure_parts.append(f"データ属性要素: {len(data_elements)}個")

        return "\n".join(structure_parts) if structure_parts else "HTML構造を特定できません"

    def _parse_selector_response(self, response_text: str) -> Dict[str, str]:
        """セレクタ生成レスポンスを解析

        Args:
            response_text: LLMからのレスポンステキスト

        Returns:
            Dict[str, str]: キーとセレクタのマッピング
        """
        try:
            # JSONブロックを抽出
            json_text = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"セレクタレスポンスの解析エラー: {str(e)}")
            raise ValueError("セレクタレスポンスの解析に失敗しました")

    def _parse_validation_response(self, response_text: str) -> bool:
        """データ検証レスポンスを解析

        Args:
            response_text: LLMからのレスポンステキスト

        Returns:
            bool: 検証結果
        """
        try:
            # JSONブロックを抽出
            json_text = response_text.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_text)
            return result.get("is_valid", False)
        except Exception as e:
            logger.error(f"検証レスポンスの解析エラー: {str(e)}")
            raise ValueError("検証レスポンスの解析に失敗しました")

    async def generate_selectors(self, html: str, target_data: Dict[str, Any]) -> Dict[str, str]:
        """HTMLからデータ抽出用のセレクタを生成

        Args:
            html: HTMLコンテンツ
            target_data: 抽出対象のデータ（キーと期待値の辞書）

        Returns:
            Dict[str, str]: キーとセレクタのマッピング
        """
        if not self.llm:
            raise ValueError("LLM model is not initialized")

        # HTMLを解析してテキストノードを抽出
        soup = BeautifulSoup(html, "html.parser")
        text_nodes = []
        for node in soup.find_all(text=True):
            text = node.get_text(strip=True)
            if text and len(text) > 1:  # 空白や1文字のテキストは除外
                # 親要素のパスも含めて保存
                text_nodes.append({
                    'text': text,
                    'node': node.parent,
                    'path': self._get_node_path(node.parent)
                })

        # 各データ項目に対してセレクタを生成
        selectors = {}
        for key, expected_value in target_data.items():
            # 最も類似度の高いテキストノードを探す
            best_match = None
            best_score = 0
            for node_info in text_nodes:
                text = node_info['text']
                # 完全一致を優先
                if expected_value == text:
                    best_match = node_info['node']
                    break
                # 部分一致の場合はスコアを計算
                elif expected_value in text or text in expected_value:
                    # 文字列の長さと位置を考慮してスコアを計算
                    common_length = len(set(expected_value) & set(text))
                    total_length = len(set(expected_value) | set(text))
                    score = common_length / total_length
                    # テーブルヘッダーやラベル要素の場合はスコアを上げる
                    if node_info['node'].name in ['th', 'td', 'label', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        score *= 1.5
                    if score > best_score:
                        best_match = node_info['node']
                        best_score = score

            if best_match:
                # ノードからCSSセレクタを生成
                selector = self._generate_css_selector(best_match)
                selectors[key] = selector

        return selectors

    def _get_node_path(self, element: Any) -> str:
        """要素のDOMパスを取得

        Args:
            element: BeautifulSoupの要素

        Returns:
            str: DOMパス
        """
        path = []
        current = element
        while current and hasattr(current, 'name') and current.name:
            # タグ名を取得
            tag_name = current.name
            # クラスがある場合は追加
            if current.get('class'):
                tag_name += '.' + '.'.join(current['class'])
            # IDがある場合は追加
            if current.get('id'):
                tag_name += f'#{current["id"]}'
            path.append(tag_name)
            current = current.parent
        return ' > '.join(reversed(path))

    def _generate_css_selector(self, element: Any) -> str:
        """要素に対するCSSセレクタを生成

        Args:
            element: BeautifulSoupの要素

        Returns:
            str: CSSセレクタ
        """
        # IDがある場合はそれを使用
        if element.get("id"):
            return f"#{element['id']}"

        # クラスがある場合はそれを使用
        if element.get("class"):
            return f".{'.'.join(element['class'])}"

        # 親要素のコンテキストを考慮したセレクタを生成
        path = []
        current = element
        max_ancestors = 3  # 最大3階層まで遡る

        while current and len(path) < max_ancestors:
            # タグ名を取得
            selector = current.name

            # 同じ階層の同じタグの中での位置を特定
            if current.parent:
                siblings = current.parent.find_all(current.name, recursive=False)
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    selector += f":nth-of-type({index})"

            path.append(selector)
            current = current.parent

        return ' > '.join(reversed(path))

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
            bool: 検証結果
        """
        if not self.llm:
            raise ValueError("LLMが初期化されていません")

        # LLMにデータを送信して検証
        prompt = self._create_validation_prompt(extracted_data, target_data)
        try:
            response = await self.llm.generate(prompt)
            return self._parse_validation_response(response)
        except Exception as e:
            logger.error(f"データ検証エラー: {str(e)}")
            raise
