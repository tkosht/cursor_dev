"""
基本モデルモジュール

このモジュールは、すべてのモデルの基底クラスを定義します。
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    """
    モデルの基底クラス

    Attributes:
        id (int): 主キー
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
    """

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        テーブル名を自動生成します。
        クラス名をスネークケースに変換します。

        Returns:
            str: テーブル名
        """
        return cls.__name__.lower()

    def to_dict(self) -> Dict[str, Any]:
        """
        モデルを辞書に変換します。

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """
        辞書からモデルを作成します。

        Args:
            data (Dict[str, Any]): モデルデータの辞書

        Returns:
            Base: 作成されたモデルインスタンス
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__table__.columns})

    def update(self, data: Dict[str, Any]) -> None:
        """
        モデルを更新します。

        Args:
            data (Dict[str, Any]): 更新データの辞書
        """
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
