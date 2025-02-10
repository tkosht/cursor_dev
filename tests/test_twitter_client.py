"""TwitterClientのテスト"""

import json
import os
from datetime import datetime

import psutil
import pytest

from app.twitter_client import TwitterClient, TwitterClientError


@pytest.fixture
def bookmarks_file(tmp_path):
    """一時的なブックマークファイルを作成"""
    return str(tmp_path / "bookmarks.json")


@pytest.fixture
def client(bookmarks_file):
    """テスト用のTwitterClientインスタンス"""
    return TwitterClient(bookmarks_file=bookmarks_file)


@pytest.fixture
def sample_bookmarks():
    """サンプルブックマークデータ"""
    return [
        {
            "id": "1234567890",
            "url": "https://twitter.com/user/status/1234567890",
            "text": "テストツイート1",
            "created_at": "1234567890",
        },
        {
            "id": "1234567891",
            "url": "https://twitter.com/user/status/1234567891",
            "text": "テストツイート2",
            "created_at": "1234567891",
        },
        {
            "id": "1234567892",
            "url": "https://twitter.com/user/status/1234567892",
            "text": "テストツイート3",
            "created_at": "1234567892",
        },
    ]


@pytest.fixture
def sample_html(tmp_path):
    """サンプルのブックマークHTMLファイルを作成"""
    html_content = """
    <!DOCTYPE NETSCAPE-Bookmark-file-1>
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
    <DL><p>
        <DT><A HREF="https://twitter.com/user/status/1234567890" ADD_DATE="1234567890">テストツイート1</A>
        <DT><A HREF="https://twitter.com/user/status/1234567891" ADD_DATE="1234567891">テストツイート2</A>
        <DT><A HREF="https://twitter.com/user/status/1234567892" ADD_DATE="1234567892">テストツイート3</A>
    </DL><p>
    """
    html_file = tmp_path / "bookmarks.html"
    html_file.write_text(html_content, encoding='utf-8')
    return str(html_file)


def test_init_creates_empty_file(bookmarks_file):
    """初期化時に空のブックマークファイルが作成されることを確認"""
    client = TwitterClient(bookmarks_file=bookmarks_file)
    assert os.path.exists(bookmarks_file)
    with open(bookmarks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 0
    assert client.bookmarks_file == bookmarks_file  # clientを使用


@pytest.mark.asyncio
async def test_import_bookmarks_html(client, sample_html):
    """HTMLファイルからのインポートが正常に動作することを確認"""
    bookmarks = await client.import_bookmarks_html(sample_html)
    assert len(bookmarks) == 3
    assert bookmarks[0]["id"] == "1234567890"
    assert bookmarks[0]["text"] == "テストツイート1"
    assert bookmarks[0]["created_at"] == "1234567890"


@pytest.mark.asyncio
async def test_import_invalid_html(client, tmp_path):
    """無効なHTMLファイルのインポート時のエラーハンドリングを確認"""
    invalid_html = tmp_path / "invalid.html"
    invalid_html.write_text("Invalid HTML", encoding='utf-8')
    
    with pytest.raises(TwitterClientError) as exc_info:
        await client.import_bookmarks_html(str(invalid_html))
    assert "HTMLファイルのインポートに失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_bookmarks(client, sample_bookmarks):
    """ブックマークの取得が正常に動作することを確認"""
    # サンプルデータを保存
    with open(client.bookmarks_file, 'w', encoding='utf-8') as f:
        json.dump(sample_bookmarks, f)
    
    # 全件取得
    bookmarks = await client.get_bookmarks()
    assert len(bookmarks) == 3
    
    # 件数制限付きで取得
    bookmarks = await client.get_bookmarks(max_results=2)
    assert len(bookmarks) == 2


@pytest.mark.asyncio
async def test_get_bookmark_updates(client, sample_bookmarks):
    """更新されたブックマークの取得が正常に動作することを確認"""
    # サンプルデータを保存
    with open(client.bookmarks_file, 'w', encoding='utf-8') as f:
        json.dump(sample_bookmarks, f)
    
    # 全件が対象の場合
    since = datetime.fromtimestamp(1234567889)
    updates = await client.get_bookmark_updates(since)
    assert len(updates) == 3
    
    # 一部のみ対象の場合
    since = datetime.fromtimestamp(1234567891)
    updates = await client.get_bookmark_updates(since)
    assert len(updates) == 2
    
    # 対象が無い場合
    since = datetime.fromtimestamp(1234567893)
    updates = await client.get_bookmark_updates(since)
    assert len(updates) == 0


@pytest.mark.asyncio
async def test_add_bookmark(client):
    """新規ブックマークの追加が正常に動作することを確認"""
    bookmark = await client.add_bookmark(
        url="https://twitter.com/user/status/1234567890",
        text="テストツイート"
    )
    assert bookmark["id"] == "1234567890"
    assert bookmark["text"] == "テストツイート"
    assert "created_at" in bookmark
    
    # ファイルに保存されていることを確認
    with open(client.bookmarks_file, 'r', encoding='utf-8') as f:
        saved_bookmarks = json.load(f)
        assert len(saved_bookmarks) == 1
        assert saved_bookmarks[0]["id"] == "1234567890"


def test_load_invalid_json(client):
    """無効なJSONファイルの読み込み時のエラーハンドリングを確認"""
    with open(client.bookmarks_file, 'w', encoding='utf-8') as f:
        f.write("Invalid JSON")
    
    with pytest.raises(TwitterClientError) as exc_info:
        client._load_bookmarks()
    assert "ブックマークファイルの解析に失敗" in str(exc_info.value)


def test_save_to_invalid_path(tmp_path):
    """無効なパスへの保存時のエラーハンドリングを確認"""
    invalid_path = str(tmp_path / "invalid" / "bookmarks.json")
    client = TwitterClient(bookmarks_file=invalid_path)
    
    # 空のブックマークリストを保存しようとする
    with pytest.raises(TwitterClientError) as exc_info:
        client._save_bookmarks([])
    assert "保存先ディレクトリが存在しません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_operations(client):
    """並行操作時の整合性を確認"""
    # 同時に複数のブックマークを追加
    import asyncio
    tasks = []
    for i in range(5):
        task = client.add_bookmark(
            url=f"https://twitter.com/user/status/{i}",
            text=f"テストツイート{i}"
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    # 全てのブックマークが保存されていることを確認
    bookmarks = await client.get_bookmarks()
    assert len(bookmarks) == 5


@pytest.mark.asyncio
async def test_large_bookmarks_performance(client):
    """大量のブックマーク処理時のパフォーマンスを確認"""
    # 1000件のブックマークを追加
    for i in range(1000):
        await client.add_bookmark(
            url=f"https://twitter.com/user/status/{i}",
            text=f"テストツイート{i}"
        )
    
    # 全件取得の時間を計測
    import time
    start_time = time.time()
    bookmarks = await client.get_bookmarks(max_results=1000)
    end_time = time.time()
    
    assert len(bookmarks) == 1000
    assert end_time - start_time < 1.0  # 1秒以内に完了すべき


def test_file_permission_error(client, tmp_path):
    """ファイルパーミッションエラーのハンドリングを確認"""
    # 読み取り専用のファイルを作成
    readonly_file = tmp_path / "readonly.json"
    readonly_file.write_text("[]")
    os.chmod(str(readonly_file), 0o444)  # 読み取り専用に設定
    
    client = TwitterClient(bookmarks_file=str(readonly_file))
    with pytest.raises(TwitterClientError) as exc_info:
        client._save_bookmarks([])
    assert "ブックマークファイルの保存に失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_url(client):
    """無効なURLのハンドリングを確認"""
    invalid_urls = [
        "",  # 空文字列
        "not_a_url",  # URLでない文字列
        "http://",  # スキームのみ
        "https://twitter.com",  # ステータスIDなし
    ]
    
    for url in invalid_urls:
        with pytest.raises(TwitterClientError) as exc_info:
            await client.add_bookmark(url=url, text="テスト")
        assert "無効なURL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_empty_text(client):
    """空のテキストのハンドリングを確認"""
    empty_texts = [
        "",  # 空文字列
        " ",  # スペースのみ
        "\n",  # 改行のみ
        "\t",  # タブのみ
    ]
    
    for text in empty_texts:
        with pytest.raises(TwitterClientError) as exc_info:
            await client.add_bookmark(
                url="https://twitter.com/user/status/1234567890",
                text=text
            )
        assert "テキストが空です" in str(exc_info.value)


def test_memory_usage(client):
    """メモリ使用量を確認"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # 大量のブックマークを保存
    bookmarks = []
    for i in range(10000):
        bookmarks.append({
            "id": str(i),
            "url": f"https://twitter.com/user/status/{i}",
            "text": f"テストツイート{i}",
            "created_at": str(i),
        })
    
    client._save_bookmarks(bookmarks)
    loaded_bookmarks = client._load_bookmarks()
    
    # メモリ使用量の増加を確認
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 1ブックマークあたりの平均メモリ使用量を計算（バイト）
    avg_memory_per_bookmark = memory_increase / len(loaded_bookmarks)
    
    # 1ブックマークあたり1KB以下であることを確認
    assert avg_memory_per_bookmark < 1024, "メモリ使用量が想定より多い"
    # 読み込んだブックマークの件数を確認
    assert len(loaded_bookmarks) == len(bookmarks), "ブックマークの件数が一致しない"


def test_error_messages(client):
    """エラーメッセージの詳細を確認"""
    # ファイルが存在しない場合
    with pytest.raises(TwitterClientError) as exc_info:
        client._load_bookmarks()
    assert "ブックマークファイルの読み込みに失敗" in str(exc_info.value)
    
    # 無効なJSONの場合
    with open(client.bookmarks_file, 'w', encoding='utf-8') as f:
        f.write("{invalid json}")
    with pytest.raises(TwitterClientError) as exc_info:
        client._load_bookmarks()
    assert "ブックマークファイルの解析に失敗" in str(exc_info.value)
    
    # 保存先ディレクトリが存在しない場合
    invalid_path = "/nonexistent/bookmarks.json"
    client = TwitterClient(bookmarks_file=invalid_path)
    with pytest.raises(TwitterClientError) as exc_info:
        client._save_bookmarks([])
    assert "保存先ディレクトリが存在しません" in str(exc_info.value) 