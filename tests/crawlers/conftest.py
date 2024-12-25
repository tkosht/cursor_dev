"""
クローラーテストの共通設定

このモジュールは、クローラーテストで使用する共通の設定やフィクスチャを提供します。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


@pytest.fixture(scope="function")
def engine():
    """
    テスト用のSQLiteインメモリデータベースエンジンを作成します。
    """
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session(engine):
    """
    テスト用のデータベースセッションを作成します。
    """
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine) 