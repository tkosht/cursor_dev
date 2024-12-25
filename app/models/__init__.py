"""
データモデルパッケージ

このパッケージは、アプリケーションで使用するデータモデルを定義します。
SQLAlchemyを使用してORMモデルを実装しています。
"""

from typing import Optional

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


# グローバルなデータベースセッション
_session: Optional[Session] = None


def get_session() -> Session:
    """
    現在のデータベースセッションを取得します。

    Returns:
        Session: 現在のデータベースセッション
    
    Raises:
        RuntimeError: セッションが初期化されていない場合
    """
    if _session is None:
        raise RuntimeError("Database session is not initialized")
    return _session


def set_session(session: Session) -> None:
    """
    データベースセッションを設定します。

    Args:
        session (Session): 設定するデータベースセッション
    """
    global _session
    _session = session 