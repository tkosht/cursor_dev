"""TwitterClientのテスト"""

import json
import os
from datetime import datetime, timedelta

import pytest

from app.twitter_client import TwitterClient, TwitterClientError


@pytest.fixture
def temp_bookmarks_file(tmp_path):
    """一時的なブックマークファイルを作成"""
    return str(tmp_path / "bookmarks.json")


@pytest.fixture
def client(temp_bookmarks_file):
    """テスト用のTwitterClientインスタンス"""
    return TwitterClient(bookmarks_file=temp_bookmarks_file)


@pytest.fixture
def sample_bookmarks():
    """サンプルブックマークデータ"""
    return [
        {
            "id": "1234567890",
            "url": "https://twitter.com/user/status/1234567890",
            "text": "テストツイート1",
            "created_at": str(datetime.now().timestamp()),
        },
        {
            "id": "9876543210",
            "url": "https://twitter.com/user/status/9876543210",
            "text": "テストツイート2",
            "created_at": str((datetime.now() - timedelta(days=1)).timestamp()),
        },
    ]


def test_init_creates_empty_bookmarks_file(temp_bookmarks_file):
    """初期化時に空のブックマークファイルが作成されることを確認"""
    TwitterClient(bookmarks_file=temp_bookmarks_file)
    assert os.path.exists(temp_bookmarks_file)
    with open(temp_bookmarks_file, "r", encoding="utf-8") as f:
        assert json.load(f) == []


def test_save_and_load_bookmarks(client, sample_bookmarks):
    """ブックマークの保存と読み込みが正常に動作することを確認"""
    client._save_bookmarks(sample_bookmarks)
    loaded_bookmarks = client._load_bookmarks()
    assert loaded_bookmarks == sample_bookmarks


@pytest.mark.asyncio
async def test_get_bookmarks(client, sample_bookmarks):
    """get_bookmarksが正常に動作することを確認"""
    client._save_bookmarks(sample_bookmarks)
    bookmarks = await client.get_bookmarks()
    assert len(bookmarks) == 2
    assert bookmarks[0]["id"] == "1234567890"


@pytest.mark.asyncio
async def test_get_bookmarks_with_max_results(client, sample_bookmarks):
    """get_bookmarksのmax_results制限が正常に動作することを確認"""
    client._save_bookmarks(sample_bookmarks)
    bookmarks = await client.get_bookmarks(max_results=1)
    assert len(bookmarks) == 1
    assert bookmarks[0]["id"] == "1234567890"


@pytest.mark.asyncio
async def test_get_bookmark_updates(client, sample_bookmarks):
    """get_bookmark_updatesが正常に動作することを確認"""
    client._save_bookmarks(sample_bookmarks)
    since = datetime.now() - timedelta(hours=12)
    updates = await client.get_bookmark_updates(since)
    assert len(updates) == 1
    assert updates[0]["id"] == "1234567890"


@pytest.mark.asyncio
async def test_add_bookmark(client):
    """add_bookmarkが正常に動作することを確認"""
    url = "https://twitter.com/user/status/1234567890"
    text = "新しいブックマーク"
    bookmark = await client.add_bookmark(url, text)
    assert bookmark["url"] == url
    assert bookmark["text"] == text
    assert "created_at" in bookmark

    # 保存されていることを確認
    bookmarks = client._load_bookmarks()
    assert len(bookmarks) == 1
    assert bookmarks[0]["url"] == url


def test_load_bookmarks_error(temp_bookmarks_file):
    """不正なJSONファイルを読み込もうとした時のエラーハンドリングを確認"""
    client = TwitterClient(bookmarks_file=temp_bookmarks_file)
    with open(temp_bookmarks_file, "w", encoding="utf-8") as f:
        f.write("invalid json")
    
    with pytest.raises(TwitterClientError) as exc_info:
        client._load_bookmarks()
    assert "ブックマークファイルの解析に失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_import_bookmarks_html(client, tmp_path):
    """HTMLからのインポートが正常に動作することを確認"""
    # テスト用のHTMLファイルを作成
    html_content = """
    <html>
    <body>
    <a href="https://twitter.com/user/status/1234567890" add_date="1234567890">テストツイート1</a>
    <a href="https://twitter.com/user/status/9876543210" add_date="9876543210">テストツイート2</a>
    </body>
    </html>
    """
    html_file = tmp_path / "bookmarks.html"
    html_file.write_text(html_content, encoding="utf-8")

    bookmarks = await client.import_bookmarks_html(str(html_file))
    assert len(bookmarks) == 2
    assert bookmarks[0]["text"] == "テストツイート1"
    assert bookmarks[1]["text"] == "テストツイート2" 
