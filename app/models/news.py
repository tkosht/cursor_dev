"""
ニュース情報モデル

このモジュールは、企業のニュース情報を管理するモデルを定義します。
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class News(BaseModel):
    """
    ニュース情報モデル

    Attributes:
        company_id (int): 企業ID（外部キー）
        title (str): ニュースタイトル
        content (str): ニュース本文
        url (str): ニュースURL
        published_at (datetime): 公開日時
        source (str): 情報ソース（例: 日経新聞、プレスリリースなど）
        category (str): カテゴリ（例: IR情報、プレスリリース、ニュースなど）
        company (Company): 企業情報への参照
    """

    company_id = Column(Integer, ForeignKey('company.id'), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), nullable=False)
    published_at = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False)
    category = Column(String(50))

    # リレーションシップ
    company = relationship("Company", back_populates="news")

    def __repr__(self) -> str:
        """
        モデルの文字列表現を返します。

        Returns:
            str: モデルの文字列表現
        """
        return (
            f"<News("
            f"company_id={self.company_id}, "
            f"title={self.title[:30]}..."
            f")>"
        ) 