"""パフォーマンステスト用の共通設定"""

from unittest.mock import Mock, patch

import pytest


def pytest_configure(config):
    """パフォーマンステスト用のマーカーを登録"""
    config.addinivalue_line(
        "markers", "performance: パフォーマンステストを示すマーカー"
    )
    config.addinivalue_line("markers", "stability: 安定性テストを示すマーカー")


@pytest.fixture(scope="session")
def large_dataset():
    """100件のテストデータを生成（セッション全体で再利用）"""
    return [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": f"テストツイート {i}",  # テキストを短縮
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(100)  # 1000から100に削減
    ]


@pytest.fixture(scope="session")
def mock_transformer():
    """SentenceTransformerのモック（セッション全体で再利用）"""
    with patch('sentence_transformers.SentenceTransformer', autospec=True) as mock:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1] * 768]
        mock.return_value = mock_model
        yield mock
