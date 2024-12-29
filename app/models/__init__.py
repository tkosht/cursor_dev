"""
デデルパッケージ

このパッケージは、アプリケーションのデータモデルを定義します。
"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

# データベースエンジンの作成
engine = create_engine("sqlite:///:memory:", echo=True)

# セッションの作成
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# ベースモデルの作成
Base = declarative_base()
Base.query = SessionLocal.query_property()

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
