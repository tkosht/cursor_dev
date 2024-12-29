"""
モニタリング機能のE2Eテスト

実際のクローラー実行時のモニタリング機能をテストします。
"""

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.crawlers.company import CompanyCrawler
from app.models.base import Base
from app.monitoring.monitor import CrawlerMonitor


@pytest.fixture
def temp_log_file():
    """一時ログファイルを作成"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def db_session():
    """テスト用DBセッション"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_crawler_monitoring(db_session: Session, temp_log_file: str):
    """クローラー実行時のモニタリングテスト"""
    # モニターの初期化
    monitor = CrawlerMonitor(log_file=temp_log_file)

    # クローラーの実行
    company_code = "9843"
    crawler = CompanyCrawler(company_code, session=db_session, monitor=monitor)

    # クローラーの状態を確認
    assert company_code not in monitor.get_active_crawlers()

    # クロール実行
    try:
        crawler.crawl()

        # クロール完了後の状態を確認
        assert company_code not in monitor.get_active_crawlers()

        # ログファイルの内容を確認
        with open(temp_log_file, "r") as f:
            log_content = f.read()
            assert "Started crawler for company 9843" in log_content
            assert "Stopped crawler for company 9843" in log_content
            assert "Progress for company 9843" in log_content
    except Exception:
        # エラー時のログを確認
        with open(temp_log_file, "r") as f:
            log_content = f.read()
            assert "Error in crawler for company 9843" in log_content
        raise


def test_multiple_crawler_monitoring(db_session: Session, temp_log_file: str):
    """複数クローラーの同時実行モニタリングテスト"""
    # モニターの初期化
    monitor = CrawlerMonitor(log_file=temp_log_file)

    # 複数のクローラーを作成
    crawlers = [
        CompanyCrawler("9843", session=db_session, monitor=monitor),
        CompanyCrawler("7203", session=db_session, monitor=monitor),
        CompanyCrawler("6758", session=db_session, monitor=monitor),
    ]

    # 各クローラーを実行
    for crawler in crawlers:
        try:
            crawler.crawl()
        except Exception:
            continue

    # 全てのクローラーが終了していることを確認
    assert len(monitor.get_active_crawlers()) == 0

    # ログファイルの内容を確認
    with open(temp_log_file, "r") as f:
        log_content = f.read()
        # 各クローラーの開始と終了が記録されていることを確認
        for code in ["9843", "7203", "6758"]:
            assert f"Started crawler for company {code}" in log_content
            assert f"Stopped crawler for company {code}" in log_content


def test_error_handling_monitoring(db_session: Session, temp_log_file: str):
    """エラー発生時のモニタリングテスト"""
    # モニターの初期化
    monitor = CrawlerMonitor(log_file=temp_log_file)

    # 存在しない企業コードでクローラーを実行
    company_code = "0000"
    crawler = CompanyCrawler(company_code, session=db_session, monitor=monitor)

    try:
        crawler.crawl()
    except Exception:
        pass

    # クローラーが終了していることを確認
    assert company_code not in monitor.get_active_crawlers()

    # ログファイルの内容を確認
    with open(temp_log_file, "r") as f:
        log_content = f.read()
        assert "Started crawler for company 0000" in log_content
        assert "Error in crawler for company 0000" in log_content
        assert "Stopped crawler for company 0000 with status error" in log_content
