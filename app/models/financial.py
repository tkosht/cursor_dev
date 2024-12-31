"""
財務情報モデル

このモジュールは、企業の財務情報を管理するモデルを定義します。
"""

from enum import Enum

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class PeriodType(str, Enum):
    """期間区分を表す列挙型"""
    FULL_YEAR = "FULL_YEAR"  # 通期
    Q1 = "Q1"  # 第1四半期
    Q2 = "Q2"  # 第2四半期
    Q3 = "Q3"  # 第3四半期
    Q4 = "Q4"  # 第4四半期


class Financial(Base):
    """
    財務情報モデル

    Attributes:
        id (int): 主キー
        company_id (int): 企業ID（外部キー）
        fiscal_year (str): 会計年度
        period_type (PeriodType): 期間区分（通期/四半期）
        period_end_date (date): 期末日
        revenue (float): 売上高
        operating_income (float): 営業利益
        net_income (float): 当期純利益
        total_assets (float): 総資産
        net_assets (float): 純資産
        cash_flow (float): キャッシュフロー
        report_date (date): 報告日
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
        company (Company): 企業情報
    """

    __tablename__ = "financial"

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    fiscal_year = Column(String(10), nullable=False)
    period_type = Column(String(20), nullable=False)
    period_end_date = Column(Date, nullable=False)
    revenue = Column(Float)
    operating_income = Column(Float)
    net_income = Column(Float)
    total_assets = Column(Float)
    net_assets = Column(Float)
    cash_flow = Column(Float)
    report_date = Column(Date)

    # リレーションシップ
    company = relationship("Company", back_populates="financials")

    def __repr__(self) -> str:
        return f"<Financial(company_id={self.company_id}, fiscal_year={self.fiscal_year})>"
