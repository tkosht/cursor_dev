"""
財務情報モデル

このモジュールは、企業の財務情報を管理するモデルを定義します。
"""

import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class PeriodType(str, enum.Enum):
    """決算期間の種類"""
    FULL_YEAR = "full_year"  # 通期
    HALF_YEAR = "half_year"  # 半期
    QUARTER = "quarter"      # 四半期


class Financial(BaseModel):
    """
    財務情報モデル

    Attributes:
        company_id (int): 企業ID（外部キー）
        fiscal_year (int): 会計年度
        period_type (PeriodType): 決算期間の種類
        period_end_date (date): 決算期間終了日
        revenue (Decimal): 売上高
        operating_income (Decimal): 営業利益
        ordinary_income (Decimal): 経常利益
        net_income (Decimal): 当期純利益
        total_assets (Decimal): 総資産
        net_assets (Decimal): 純資産
        earnings_per_share (Decimal): 1株当たり当期純利益
        book_value_per_share (Decimal): 1株当たり純資産
        dividend_per_share (Decimal): 1株当たり配当金
        company (Company): 企業情報への参照
    """

    company_id = Column(Integer, ForeignKey('company.id'), nullable=False, index=True)
    fiscal_year = Column(String(10), nullable=False)  # 2023年度、2023Q1などの表記に対応するため文字列で保存
    period_type = Column(Enum(PeriodType), nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # 金額はすべて千円単位で保存
    revenue = Column(Numeric(20, 2))  # 売上高
    operating_income = Column(Numeric(20, 2))  # 営業利益
    ordinary_income = Column(Numeric(20, 2))  # 経常利益
    net_income = Column(Numeric(20, 2))  # 当期純利益
    total_assets = Column(Numeric(20, 2))  # 総資産
    net_assets = Column(Numeric(20, 2))  # 純資産
    
    # 1株当たり情報は小数点以下2桁まで保存
    earnings_per_share = Column(Numeric(10, 2))  # EPS
    book_value_per_share = Column(Numeric(10, 2))  # BPS
    dividend_per_share = Column(Numeric(10, 2))  # 配当金

    # リレーションシップ
    company = relationship("Company", back_populates="financials")

    def __repr__(self) -> str:
        """
        モデルの文字列表現を返します。

        Returns:
            str: モデルの文字列表現
        """
        return (
            f"<Financial("
            f"company_id={self.company_id}, "
            f"fiscal_year={self.fiscal_year}, "
            f"period_type={self.period_type.value}"
            f")>"
        ) 