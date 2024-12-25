"""
企業情報モデル

このモジュールは、企業の基本情報を管理するモデルを定義します。
"""

from typing import List

from sqlalchemy import Column, Date, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .financial import Financial
from .news import News


class Company(BaseModel):
    """
    企業情報モデル

    Attributes:
        company_code (str): 企業コード（証券コードなど）
        name (str): 企業名
        name_en (str): 企業名（英語）
        established_date (date): 設立日
        description (str): 企業概要
        headquarters_address (str): 本社所在地
        representative_name (str): 代表者名
        representative_position (str): 代表者役職
        website_url (str): WebサイトURL
        stock_exchange (str): 上場取引所
        industry (str): 業種
        employees_count (int): 従業員数
        financials (List[Financial]): 財務情報のリスト
        news (List[News]): ニュース情報のリスト
    """

    company_code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    established_date = Column(Date)
    description = Column(Text)
    headquarters_address = Column(String(255))
    representative_name = Column(String(100))
    representative_position = Column(String(100))
    website_url = Column(String(255))
    stock_exchange = Column(String(50))
    industry = Column(String(100))
    employees_count = Column(String(20))  # 数値��場合もあれば「約○○名」という表記の場合もあるため文字列で保存

    # リレーションシップ
    financials = relationship("Financial", back_populates="company", cascade="all, delete-orphan")
    news = relationship("News", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """
        モデルの文字列表現を返します。

        Returns:
            str: モデルの文字列表現
        """
        return f"<Company(code={self.company_code}, name={self.name})>" 