"""
テストフィクスチャの定義
"""
import os
import tempfile
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """テスト用DBセッションを提供するフィクスチャ"""
    # テスト用の一時DBファイルを作成
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    
    # エンジンとセッションを作成
    engine = create_engine(db_url, echo=True)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    
    # テーブルを作成
    Base.metadata.drop_all(bind=engine)  # 既存のテーブルを削除
    Base.metadata.create_all(bind=engine)  # 新しいテーブルを作成
    
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()
        os.close(db_fd)
        os.unlink(db_path) 