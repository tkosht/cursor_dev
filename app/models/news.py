"""
ニュース情報モデル

このモジュールは、企業のニュース情報を管理するモデルを定義します。
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .company import Company


class News(Base):
    """
    ニュースモデル

    Attributes:
        id (int): 主キー
        company_id (int): 企業ID（外部キー）
        title (str): タイトル
        content (str): 本文
        url (str): ソースURL
        published_at (datetime): 公開日時
        source (str): 情報ソース
        category (str): カテゴリ
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
        company (Company): 企業
    """

    company_id = Column(BigInteger, ForeignKey("company.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    url = Column(String(255))
    published_at = Column(DateTime, nullable=False)
    source = Column(String(50))
    category = Column(String(50))

    company: Mapped["Company"] = relationship("Company", back_populates="news")

    def __repr__(self) -> str:
        return f"<News(company_id={self.company_id}, title={self.title})>"
