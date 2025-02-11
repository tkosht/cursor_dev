"""パフォーマンステスト用の共通設定"""

import pytest


def pytest_configure(config):
    """パフォーマンステスト用のマーカーを登録"""
    config.addinivalue_line(
        "markers", "performance: パフォーマンステストを示すマーカー"
    )
    config.addinivalue_line("markers", "stability: 安定性テストを示すマーカー")


@pytest.fixture(scope="session")
def large_dataset():
    """10万件のテストデータを生成（セッション全体で再利用）"""
    return [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": f"テストツイート {i} " * 10,  # 適度な長さのテキスト
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(100000)
    ]
