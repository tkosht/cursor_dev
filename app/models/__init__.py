"""
デデル定義
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 必要なモデルのみをインポート
from .company import Company  # noqa: F401
