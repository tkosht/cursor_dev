"""
pytestの共通設定
"""

import logging
import os
import sys
from pathlib import Path

import pytest  # noqa: F401 - used by pytest for test configuration

# プロジェクトルートをPYTHONPATHに追加
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# テスト用の設定
os.environ.setdefault("COMPANY_CONFIG_PATH", "app/config/companies.yaml")


def pytest_configure():
    """テストの設定"""
    # ログレベルをDEBUGに設定
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
