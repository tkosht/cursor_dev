"""
財務情報モデル

このモジュールは、企業の財務情報を管理するモデルを定義します。
"""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .company import Company


class PeriodType(str, Enum):
    FULL_YEAR = "FULL_YEAR"
    QUARTER = "QUARTER"


class Financial(Base):
    """
    財務情報モデル
    
    Attributes:
        id (int): 主キー
        company_id (int): 企業ID（外部キー）
        fiscal_year (str): 会計年度
        period_type (str): 期間区分（通期/第1四半期/第2四半期/第3四半期）
        period_end_date (date): 期末日
        revenue (int): 売上高
        operating_income (int): 営業利益
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
        company (Company): 企業
    """
    
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    fiscal_year = Column(String(10), nullable=False)
    period_type = Column(String(20), nullable=False)
    period_end_date = Column(Date, nullable=False)
    revenue = Column(BigInteger)
    operating_income = Column(BigInteger)
    
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="financials"
    )
    
    def __repr__(self) -> str:
        return f"<Financial(company_id={self.company_id}, fiscal_year={self.fiscal_year})>" 