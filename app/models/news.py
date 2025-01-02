"""News model implementation."""

import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class News(Base):
    """ニュースモデル"""

    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    url = Column(String(2048), nullable=False)
    source = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    # リレーションシップ
    company = relationship("Company", back_populates="news")

    def __str__(self) -> str:
        """文字列表現を返す"""
        return f"<News(title={self.title})>"

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "News":
        """辞書からインスタンスを作成"""
        news = cls()
        for key, value in data.items():
            if hasattr(news, key):
                if key == "published_at" and value:
                    value = datetime.datetime.fromisoformat(value)
                setattr(news, key, value)
        return news

    def update(self, data: Dict[str, Any]) -> None:
        """データを更新"""
        for key, value in data.items():
            if hasattr(self, key):
                if key == "published_at" and value:
                    value = datetime.datetime.fromisoformat(value)
                setattr(self, key, value) 