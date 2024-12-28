"""
クローラーの設定管理

YAMLファイルから企業ごとの設定を読み込みます。
"""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field


class CompanySelectors(BaseModel):
    """企業情報のセレクター設定"""
    description: str = Field(..., description='企業概要のセレクター')


class FinancialSelectors(BaseModel):
    """財務情報のセレクター設定"""
    table: str = Field(..., description='財務テーブルのセレクター')
    rows: str = Field(..., description='行のセレクター')
    columns: Dict[str, int] = Field(..., description='各項目の列インデックス')


class NewsSelectors(BaseModel):
    """ニュースのセレクター設定"""
    list: str = Field(..., description='ニュースリストのセレクター')
    date: str = Field(..., description='日付のセレクター')
    title: str = Field(..., description='タイトルのセレクター')
    link: str = Field(..., description='リンクのセレクター')


class CompanyPaths(BaseModel):
    """企業情報の各ページパス"""
    company_info: str = Field(..., description='企業情報ページのパス')
    financial_info: str = Field(..., description='財務情報ページのパス')
    news: str = Field(..., description='ニュースページのパス')


class DateFormats(BaseModel):
    """日付フォーマット設定"""
    news: str = Field(..., description='ニュースの日付フォーマット')


class CompanyConfig(BaseModel):
    """企業ごとの設定"""
    base_url: str = Field(..., description='企業サイトのベースURL')
    name: str = Field(..., description='企業名')
    stock_exchange: str = Field(..., description='上場取引所')
    industry: str = Field(..., description='業種')
    paths: CompanyPaths = Field(..., description='各ページのパス')
    selectors: Dict[str, Dict] = Field(..., description='各要素のセレクター')
    date_formats: DateFormats = Field(..., description='日付フォーマット')


class CrawlerConfig:
    """クローラーの設定管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 設定ファイルのパス
        """
        if config_path is None:
            config_path = str(
                Path(__file__).parent / 'companies.yaml'
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        self.companies: Dict[str, CompanyConfig] = {}
        for code, data in config_data['companies'].items():
            self.companies[code] = CompanyConfig(**data)
    
    def get_company_config(self, company_code: str) -> Optional[CompanyConfig]:
        """企業の設定を取得
        
        Args:
            company_code: 企業コード
        
        Returns:
            企業の設定。存在しない場合はNone
        """
        return self.companies.get(company_code)


# グローバルなインスタンス
config = CrawlerConfig()


def get_company_config(company_code: str) -> Optional[CompanyConfig]:
    """企業の設定を取得
    
    Args:
        company_code: 企業コード
    
    Returns:
        企業の設定。存在しない場合はNone
    """
    return config.get_company_config(company_code) 