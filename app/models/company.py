"""
企業情報モデル

このモジュールは、企業の基本情報を管理するモデルを定義します。
"""

from sqlalchemy import Column, Date, String, Text

from .base import Base


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
        headquarters_address (str): 本社所在地
        representative_name (str): 代表者名
        representative_position (str): 代表者役職
        employees_count (str): 従業員数
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
    """

    __tablename__ = "company"

    company_code = Column(String(4), nullable=True, unique=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    description = Column(Text)
    established_date = Column(Date)
    website_url = Column(String(255))
    stock_exchange = Column(String(50))
    industry = Column(String(50))
    headquarters_address = Column(String(255))
    representative_name = Column(String(100))
    representative_position = Column(String(100))
    employees_count = Column(String(100))

    def __repr__(self) -> str:
        return f"<Company(name={self.name})>"
