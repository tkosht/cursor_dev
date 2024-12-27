"""
クローラー設定モジュール

このモジュールは、クローラーの設定を管理します。
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class CompanyConfig:
    """企業クローラーの設定

    Attributes:
        company_code (str): 企業コード
        base_url (str): 基本URL
        company_info_path (str): 企業情報ページのパス
        financial_info_path (str): 財務情報ページのパス
        news_info_path (str): ニュースページのパス
    """
    company_code: str
    base_url: str
    company_info_path: str = "/company/"
    financial_info_path: str = "/ir/library/result.html"
    news_info_path: str = "/ir/news/"


# 企業ごとの設定
COMPANY_CONFIGS: Dict[str, CompanyConfig] = {
    "9843": CompanyConfig(
        company_code="9843",
        base_url="https://www.nitorihd.co.jp",
    ),
}


def get_company_config(company_code: str) -> Optional[CompanyConfig]:
    """
    企業コードに対応する設定を取得します。

    Args:
        company_code (str): 企業コード

    Returns:
        Optional[CompanyConfig]: 企業の設定。存在しない場合はNone
    """
    return COMPANY_CONFIGS.get(company_code) 