"""
企業情報モデル

このモジュールは、企業の基本情報を管理するモデルを定義します。
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Date, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .financial import Financial
    from .news import News


class Company(Base):
    """
    企業情報モデル

    Attributes:
        id (int): 主キー
        company_code (str): 企業コード
        name (str): 企業名
        name_en (str): 企業名（英語）
        description (str): 事業概要
        established_date (date): 設立日
        website_url (str): Webサイト
        stock_exchange (str): 上場市場
        industry (str): 業種
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
        financials (List[Financial]): 財務情報リスト
        news (List[News]): ニュースリスト
    """

    company_code = Column(String(4), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    description = Column(Text)
    established_date = Column(Date, nullable=False)
    website_url = Column(String(255))
    stock_exchange = Column(String(50))
    industry = Column(String(50))

    financials: Mapped[List["Financial"]] = relationship(
        "Financial", back_populates="company", cascade="all, delete-orphan"
    )

    news: Mapped[List["News"]] = relationship(
        "News", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(code={self.company_code}, name={self.name})>"
