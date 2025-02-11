"""TwitterClientとSearchEngineの統合テスト"""

import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from app.search_engine import SearchEngine, SearchEngineError
from app.twitter_client import TwitterClient, TwitterClientError


@pytest.fixture
def temp_dir():
    """一時ディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # テスト後にディレクトリを削除
    shutil.rmtree(temp_dir)


@pytest.fixture
def index_dir(temp_dir):
    """検索エンジンのインデックスディレクトリ"""
    return os.path.join(temp_dir, "search_index")


@pytest.fixture
def bookmarks_file(temp_dir):
    """ブックマークファイルのパス"""
    return os.path.join(temp_dir, "bookmarks.json")


@pytest.fixture
def sample_bookmarks():
    """テスト用のサンプルブックマーク"""
    return [
        {
            "id": "1",
            "url": "https://twitter.com/user1/status/1",
            "text": "Pythonプログラミングについて",
            "created_at": "1234567890",
            "author": "user1",
        },
        {
            "id": "2",
            "url": "https://twitter.com/user2/status/2",
            "text": "機械学習の基礎",
            "created_at": "1234567891",
            "author": "user2",
        },
        {
            "id": "3",
            "url": "https://twitter.com/user3/status/3",
            "text": "データ分析の手法",
            "created_at": "1234567892",
            "author": "user3",
        },
    ]


@pytest.fixture
def twitter_client(bookmarks_file):
    """TwitterClientインスタンス"""
    return TwitterClient(bookmarks_file=bookmarks_file)


@pytest.fixture
def search_engine(index_dir):
    """SearchEngineインスタンス"""
    return SearchEngine(index_dir=index_dir)


@pytest.mark.asyncio
async def test_basic_integration_flow(
    twitter_client, search_engine, sample_bookmarks
):
    """基本的な統合フローのテスト"""
    # TwitterClientにブックマークを設定
    with patch.object(
        twitter_client, "_load_bookmarks", return_value=sample_bookmarks
    ):
        bookmarks = twitter_client._load_bookmarks()

    # SearchEngineにブックマークを追加
    search_engine.add_bookmarks(bookmarks)

    # 検索を実行
    results = search_engine.search("Python")
    assert len(results) > 0
    bookmark, score = results[0]
    assert "Python" in bookmark["text"]
    assert isinstance(score, float)


@pytest.mark.asyncio
async def test_api_rate_limit(twitter_client, search_engine):
    """APIレート制限時の動作確認"""
    # APIレート制限をシミュレート
    with patch.object(
        twitter_client,
        "_load_bookmarks",
        side_effect=TwitterClientError("レート制限超過"),
    ):
        with pytest.raises(TwitterClientError) as exc_info:
            twitter_client._load_bookmarks()
        assert "レート制限超過" in str(exc_info.value)


@pytest.mark.asyncio
async def test_network_error(twitter_client, search_engine):
    """ネットワークエラー時の動作確認"""
    # ネットワークエラーをシミュレート
    with patch.object(
        twitter_client,
        "_load_bookmarks",
        side_effect=TwitterClientError("ネットワークエラー"),
    ):
        with pytest.raises(TwitterClientError) as exc_info:
            twitter_client._load_bookmarks()
        assert "ネットワークエラー" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_data_format(twitter_client, search_engine):
    """無効なデータ形式の処理確認"""
    invalid_bookmarks = [{"invalid": "data"}]

    # 無効なデータ形式をシミュレート
    with patch.object(
        twitter_client, "_load_bookmarks", return_value=invalid_bookmarks
    ):
        bookmarks = twitter_client._load_bookmarks()

        # SearchEngineでの処理を確認
        with pytest.raises(SearchEngineError) as exc_info:
            search_engine.add_bookmarks(bookmarks)
        assert "ブックマークの追加に失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_large_dataset(twitter_client, search_engine):
    """大規模データセットの処理確認"""
    # 1000件のブックマークを生成
    large_bookmarks = [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": f"テストツイート {i}",
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(1000)
    ]

    # 大規模データセットの処理
    with patch.object(
        twitter_client, "_load_bookmarks", return_value=large_bookmarks
    ):
        bookmarks = twitter_client._load_bookmarks()
        search_engine.add_bookmarks(bookmarks)

        # 検索性能を確認
        import time

        start_time = time.time()
        results = search_engine.search("テスト")
        end_time = time.time()

        assert len(results) > 0
        assert end_time - start_time < 1.0  # 1秒以内に検索完了


@pytest.mark.asyncio
async def test_error_propagation(twitter_client, search_engine):
    """エラー伝播の確認"""
    # TwitterClientのエラーが適切に伝播することを確認
    with patch.object(
        twitter_client,
        "_load_bookmarks",
        side_effect=TwitterClientError("テストエラー"),
    ):
        with pytest.raises(TwitterClientError) as exc_info:
            bookmarks = twitter_client._load_bookmarks()
            search_engine.add_bookmarks(bookmarks)
        assert "テストエラー" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_operations(
    twitter_client, search_engine, sample_bookmarks
):
    """並行処理の確認"""
    import asyncio

    # 複数の操作を並行実行
    async def concurrent_operation():
        with patch.object(
            twitter_client, "_load_bookmarks", return_value=sample_bookmarks
        ):
            bookmarks = twitter_client._load_bookmarks()
            search_engine.add_bookmarks(bookmarks)
            return search_engine.search("Python")

    # 5つの並行タスクを実行
    tasks = [concurrent_operation() for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # すべてのタスクが正常に完了することを確認
    for result in results:
        assert len(result) > 0
        assert isinstance(result[0], tuple)


@pytest.mark.asyncio
async def test_memory_usage(twitter_client, search_engine):
    """メモリ使用量の確認"""
    import psutil

    process = psutil.Process()

    # 大規模データセットを生成
    large_bookmarks = [
        {
            "id": str(i),
            "url": f"https://twitter.com/user{i}/status/{i}",
            "text": f"テストツイート {i}",
            "created_at": str(1234567890 + i),
            "author": f"user{i}",
        }
        for i in range(10000)
    ]

    # メモリ使用量を測定
    initial_memory = process.memory_info().rss

    with patch.object(
        twitter_client, "_load_bookmarks", return_value=large_bookmarks
    ):
        bookmarks = twitter_client._load_bookmarks()
        search_engine.add_bookmarks(bookmarks)

        # 検索を実行
        _ = search_engine.search("テスト")

    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB単位

    assert memory_increase < 2000  # メモリ増加は2GB以内


@pytest.mark.asyncio
async def test_data_consistency(
    twitter_client, search_engine, sample_bookmarks
):
    """データの一貫性確認"""
    # ブックマークを追加
    with patch.object(
        twitter_client, "_load_bookmarks", return_value=sample_bookmarks
    ):
        bookmarks = twitter_client._load_bookmarks()
        search_engine.add_bookmarks(bookmarks)

    # 各ブックマークが検索可能であることを確認
    for bookmark in sample_bookmarks:
        results = search_engine.search(bookmark["text"])
        assert len(results) > 0
        found = False
        for result, _ in results:
            if result["id"] == bookmark["id"]:
                found = True
                break
        assert found, f"ブックマークID {bookmark['id']} が見つかりません"
