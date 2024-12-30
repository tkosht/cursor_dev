"""
データモデルパッケージ

このパッケージは、アプリケーションのデータモデルを定義します。
"""

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from .base import Base

# データベースファイルのパスを設定
DB_FILE = "app.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", DB_FILE)

# データディレクトリが存在しない場合は作成
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# データベースエンジンの作成
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)

# セッションの作成
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# ベースモデルの設定
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


def init_db():
    """
    データベースを初期化し、全てのテーブルを作成します。
    """
    # 循環インポートを避けるためにここでインポート
    # noqa: F401 は未使用のインポートを許可するために使用
    from . import company  # noqa: F401
    from . import financial  # noqa: F401
    from . import news  # noqa: F401

    Base.metadata.create_all(bind=engine)
