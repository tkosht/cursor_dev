"""
プロンプトテンプレートの定義
"""
from typing import Dict, Optional


class PromptTemplate:
    """プロンプトテンプレートクラス"""

    def __init__(self, template: str, variables: Optional[Dict[str, str]] = None) -> None:
        """
        初期化

        Args:
            template (str): テンプレート文字列
            variables (Optional[Dict[str, str]], optional): 変数の辞書. Defaults to None.
        """
        self.template = template
        self.variables = variables or {}

    def format(self, **kwargs) -> str:
        """
        テンプレートをフォーマット

        Args:
            **kwargs: フォーマット時の変数

        Returns:
            str: フォーマットされたプロンプト
        """
        variables = {**self.variables, **kwargs}
        return self.template.format(**variables)


class PromptManager:
    """プロンプト管理クラス"""

    TEMPLATES = {
        "selector_generation": PromptTemplate(
            "HTMLから必要な情報を抽出するための最適なCSSセレ��ターを"
            "生成してください。以下のHTMLを分析し、重要な要素を特定して"
            "それらを抽出するためのセレクターを提案してください。\n\n"
            "以下の形式で出力してください：\n"
            "セレクター:\n"
            "提案するセレクター\n\n"
            "説明:\n"
            "セレクターの説明\n\n"
            "HTML:\n"
            "{content}"
        ),
        "content_extraction": PromptTemplate(
            "HTMLから情報を抽出し、構造化してください。"
            "各要素の内容を適切なキーと値のペアとして整理してください。\n\n"
            "以下の形式で出力してください：\n"
            "会社名:\n"
            "抽出された会社名\n\n"
            "住所:\n"
            "抽出された住所\n\n"
            "財務情報:\n"
            "抽出された財務情報\n\n"
            "HTML:\n"
            "{content}"
        ),
        "error_analysis": PromptTemplate(
            "エラー情報を分析し、対処方法を提案してください。"
            "エラーの原因と考えられる要因を特定し、"
            "解決のためのアプローチを提示してください。\n\n"
            "以下の形式で出力してください：\n"
            "エラー種別:\n"
            "エラーの種類\n\n"
            "原因:\n"
            "推定される原因\n\n"
            "対策:\n"
            "推奨される対処方法\n\n"
            "エラー内容:\n"
            "{content}"
        ),
        "default": PromptTemplate(
            "以下の内容を分析してください。重要な情報を抽出し、"
            "構造化された形式で結果を提示してください。\n\n"
            "以下の形式で出力してください：\n"
            "概要:\n"
            "内容の要約\n\n"
            "詳細:\n"
            "詳細な分析\n\n"
            "内容:\n"
            "{content}"
        )
    }

    @classmethod
    def get_template(cls, task: str) -> PromptTemplate:
        """
        タスクに応じたテンプレートを取得

        Args:
            task (str): タスク名

        Returns:
            PromptTemplate: プロンプトテンプレート
        """
        return cls.TEMPLATES.get(task, cls.TEMPLATES["default"])

    @classmethod
    def format_prompt(cls, task: str, content: str, **kwargs) -> str:
        """
        プロンプトをフォーマット

        Args:
            task (str): タスク名
            content (str): コンテンツ
            **kwargs: 追加の変数

        Returns:
            str: フォーマットされたプロンプト
        """
        template = cls.get_template(task)
        return template.format(content=content, **kwargs) 