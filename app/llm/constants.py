"""LLM関連の定数を定義するモジュール"""

from typing import Dict


class LLMConstants:
    """LLM関連の定数"""

    # パーサー設定
    HTML_PARSER = "html.parser"

    # URL関連
    URL_SCHEMES = ("http://", "https://")
    URL_PATTERN = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

    # HTML構造
    HTML_STRUCTURE = {
        "headings": ["h1", "h2", "h3", "h4", "h5", "h6"],
        "navigation": ["nav", "menu"],
        "main": "main",
        "footer": "footer"
    }

    # プロンプトテンプレート
    PROMPT_TEMPLATES: Dict[str, str] = {
        "pattern_generation": """
以下のセマンティック構造に基づいて、IR情報を抽出するためのパターンを生成してください。

対象タイプ: {target_type}
セマンティック構造: {semantic_structure}

以下のフォーマットでJSONを返してください:
{
    "successful_pattern": true,
    "pattern": {
        "tag": "タグ名",
        "classes": ["クラス名1", "クラス名2", ...],
        "id": "ID",
        "children": [
            {
                "tag": "子タグ名",
                "classes": ["クラス名1", "クラス名2", ...],
                "id": "子ID"
            },
            ...
        ]
    }
}
""",
        "url_extraction": """
以下のHTML要素からIR情報に関連するURLを抽出してください。

対象タイプ: {target_type}
HTML要素: {html_element}

以下のフォーマットでJSONを返してください:
{
    "successful_extraction": true,
    "urls": [
        "URL1",
        "URL2",
        ...
    ]
}
""",
        "search_keywords": """
以下の企業コードと必要なフィールドに基づいて、IR情報を検索するためのキーワードを生成してください。
キーワードは検索エンジンで使用することを想定しています。

企業コード: {company_code}
必要なフィールド: {target_fields}

以下の点を考慮してキーワードを生成してください：
1. 企業コードが実際のURLの場合は、そのドメインやパスから関連キーワードを抽出
2. 企業コードが証券コードの場合は、企業名や業界に関連するキーワードを生成
3. 必要なフィールドの特性に応じたキーワード（例：dateフィールドなら「決算発表」「IR情報」など）
4. 一般的なIR情報関連のキーワード（「プレスリリース」「適時開示」など）

以下のフォーマットでJSONを返してください:
{
    "keywords": [
        "キーワード1",
        "キーワード2",
        ...
    ]
}
""",
        "domain_validation": """
以下のドメインが企業のIR情報を提供する信頼できるソースかどうかを評価してください。

ドメイン: {domain}
企業コード: {company_code}

以下の点を考慮して評価してください：
1. 公式企業サイトかどうか
2. 証券取引所や金融機関のドメインかどうか
3. ニュースメディアや経済メディアのドメインかどうか
4. IR情報配信サービスのドメインかどうか

以下のフォーマットでJSONを返してください:
{
    "is_trusted": true/false,
    "confidence": 0.0-1.0,
    "reason": "評価理由の説明"
}
""",
        "path_evaluation": """
以下のURLのパスがIR情報に関連する可能性を評価してください。

URL: {url}

以下の点を考慮して評価してください：
1. パスにIR情報を示す要素が含まれているか（ir, investor, financial など）
2. パスに日付や時期を示す要素が含まれているか
3. パスにドキュメントタイプを示す要素が含まれているか（pdf, release など）
4. パスの深さと構造が適切か

以下のフォーマットでJSONを返してください:
{
    "relevance_score": 0.0-1.0,
    "relevant_elements": ["要素1", "要素2", ...],
    "reason": "評価理由の説明"
}
""",
        "data_reliability": """
以下の抽出データの信頼性を評価してください。

データ: {data}
ソースURL: {url}

以下の点を考慮して評価してください：
1. データの完全性（必要なフィールドが揃っているか）
2. データの形式が適切か
3. データの内容に一貫性があるか
4. データがソースURLのコンテキストと一致するか

以下のフォーマットでJSONを返してください:
{
    "reliability_score": 0.0-1.0,
    "validation_results": {
        "フィールド名": {
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "issues": ["問題点1", "問題点2", ...]
        },
        ...
    },
    "overall_assessment": "総合的な評価の説明"
}
"""
    }

    # デフォルトのプロンプトパラメータ
    DEFAULT_PROMPT_PARAMS = {
        "target_type": "IR情報",
        "semantic_structure": {
            "tag": "div",
            "classes": [],
            "id": "",
            "children": []
        },
        "html_element": {
            "tag": "a",
            "text": "",
            "href": "",
            "context": {}
        }
    }

    # 最大トークン数
    MAX_TOKENS = {
        "pattern_generation": 1000,
        "url_extraction": 500,
        "search_keywords": 300,
        "domain_validation": 500,
        "path_evaluation": 500,
        "data_reliability": 800
    }

    # 温度パラメータ
    TEMPERATURE = {
        "pattern_generation": 0.1,
        "url_extraction": 0.1,
        "search_keywords": 0.3,
        "domain_validation": 0.1,
        "path_evaluation": 0.2,
        "data_reliability": 0.1
    }

    # リトライ設定
    RETRY_CONFIG = {
        "max_retries": 3,
        "initial_delay": 1.0,
        "max_delay": 10.0,
        "backoff_factor": 2.0
    }

    # レート制限設定
    RATE_LIMIT = {
        "requests_per_minute": 60,
        "burst_size": 10
    }

    # ターゲットパス
    TARGET_PATHS = {
        "ir_info": [
            "ir", "investor", "financial", "earnings",
            "results", "disclosure", "finance"
        ],
        "company_info": [
            "company", "about", "corporate", "profile",
            "overview", "philosophy", "message"
        ],
        "financial_info": [
            "financial", "finance", "earnings", "results",
            "statements", "balance", "income", "performance",
            "highlight", "report", "quarter", "annual",
            "presentation", "briefing", "summary"
        ]
    }

    # パターン優先度
    MIN_PRIORITY = 1
    DEFAULT_PRIORITY = 3
    HIGH_PRIORITY = 5
    MAX_PRIORITY = 10

    # 評価スコア
    MIN_SCORE = 0.0
    SUCCESS_THRESHOLD = 0.7
    LOW_EFFECTIVENESS = 0.3
    HIGH_EFFECTIVENESS = 0.7

    # 信頼性スコア
    RELIABILITY_THRESHOLDS = {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.3
    }

    # ドメイン評価
    DOMAIN_CATEGORIES = {
        "official": ["co.jp", "corp", "company", "group"],
        "financial": ["jpx.co.jp", "tse.or.jp", "release.tdnet"],
        "news": ["news", "nikkei", "reuters", "bloomberg"],
        "ir_service": ["ir", "investor", "kaiji", "disclosure"]
    } 