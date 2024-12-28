"""
統合テスト用の共通設定
"""
import os

import pytest
from dotenv import load_dotenv

from app.llm.manager import LLMManager


def pytest_configure(config):
    """pytestの設定"""
    # integrationマーカーを登録
    config.addinivalue_line(
        'markers',
        'integration: mark test as integration test'
    )


@pytest.fixture(scope='session', autouse=True)
def load_env():
    """環境変数を読み込む"""
    load_dotenv()


@pytest.fixture(scope='session')
def api_key():
    """APIキーを取得"""
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        pytest.skip('GEMINI_API_KEY not set')
    return key


@pytest.fixture(scope='session')
def llm_manager(api_key):
    """LLMマネージャーのインスタンス"""
    manager = LLMManager()
    manager.load_model('gemini-2.0-flash-exp', api_key)
    return manager 