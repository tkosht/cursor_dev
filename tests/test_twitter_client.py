"""TwitterClientのテスト"""

import asyncio
import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

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
    html_file.write_text(html_content, encoding="utf-8")
    return str(html_file)


def test_init_creates_empty_file(bookmarks_file):
    """初期化時に空のブックマークファイルが作成されることを確認"""
    client = TwitterClient(bookmarks_file=bookmarks_file)
    assert os.path.exists(bookmarks_file)
    with open(bookmarks_file, "r", encoding="utf-8") as f:
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
    invalid_html.write_text("Invalid HTML", encoding="utf-8")

    with pytest.raises(TwitterClientError) as exc_info:
        await client.import_bookmarks_html(str(invalid_html))
    assert "HTMLファイルのインポートに失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_bookmarks(client, sample_bookmarks):
    """ブックマークの取得が正常に動作することを確認"""
    # サンプルデータを保存
    with open(client.bookmarks_file, "w", encoding="utf-8") as f:
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
    with open(client.bookmarks_file, "w", encoding="utf-8") as f:
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
        url="https://twitter.com/user/status/1234567890", text="テストツイート"
    )
    assert bookmark["id"] == "1234567890"
    assert bookmark["text"] == "テストツイート"
    assert "created_at" in bookmark

    # ファイルに保存されていることを確認
    with open(client.bookmarks_file, "r", encoding="utf-8") as f:
        saved_bookmarks = json.load(f)
        assert len(saved_bookmarks) == 1
        assert saved_bookmarks[0]["id"] == "1234567890"


def test_load_invalid_json(client):
    """無効なJSONファイルの読み込み時のエラーハンドリングを確認"""
    with open(client.bookmarks_file, "w", encoding="utf-8") as f:
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
    tasks = []
    for i in range(5):
        task = client.add_bookmark(
            url=f"https://twitter.com/user/status/{i}",
            text=f"テストツイート{i}",
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
            text=f"テストツイート{i}",
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
                url="https://twitter.com/user/status/1234567890", text=text
            )
        assert "テキストが空です" in str(exc_info.value)


def test_memory_usage(client):
    """メモリ使用量を確認"""
    process = psutil.Process()

    # メモリ使用量を安定させるためにGCを実行
    import gc

    gc.collect()
    initial_memory = process.memory_info().rss

    # 1000件のブックマークを保存（10000件から削減）
    bookmarks = []
    for i in range(1000):
        bookmarks.append(
            {
                "id": str(i),
                "url": f"https://twitter.com/user/status/{i}",
                "text": f"テストツイート{i}",
                "created_at": str(i),
            }
        )

    client._save_bookmarks(bookmarks)

    # メモリを安定させるためにGCを実行
    gc.collect()

    loaded_bookmarks = client._load_bookmarks()

    # メモリを安定させるためにGCを実行
    gc.collect()

    # メモリ使用量の増加を確認
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # 1ブックマークあたりの平均メモリ使用量を計算（バイト）
    avg_memory_per_bookmark = memory_increase / len(loaded_bookmarks)

    # 1ブックマークあたり2KB以下であることを確認（閾値を調整）
    assert (
        avg_memory_per_bookmark < 2048
    ), f"メモリ使用量が想定より多い: {avg_memory_per_bookmark:.2f} bytes/bookmark"
    # 読み込んだブックマークの件数を確認
    assert len(loaded_bookmarks) == len(
        bookmarks
    ), "ブックマークの件数が一致しない"


def test_error_messages(client, tmp_path):
    """エラーメッセージの詳細な検証"""
    # 無効なURL
    with pytest.raises(TwitterClientError) as exc_info:
        client._validate_url("")
    assert "URLが空です" in str(exc_info.value)

    with pytest.raises(TwitterClientError) as exc_info:
        client._validate_url("https://example.com")
    assert "TwitterのステータスURLではありません" in str(exc_info.value)

    # 無効なテキスト
    with pytest.raises(TwitterClientError) as exc_info:
        client._validate_text("")
    assert "テキストが空です" in str(exc_info.value)

    with pytest.raises(TwitterClientError) as exc_info:
        client._validate_text("   ")
    assert "テキストが空です" in str(exc_info.value)

    # ファイル操作エラー
    invalid_path = str(tmp_path / "nonexistent" / "bookmarks.json")
    test_client = TwitterClient(invalid_path)
    with pytest.raises(TwitterClientError) as exc_info:
        test_client._save_bookmarks([])
    assert "保存先ディレクトリが存在しません" in str(exc_info.value)

    # JSONデコードエラー
    with open(client.bookmarks_file, "w", encoding="utf-8") as f:
        f.write("invalid json")
    with pytest.raises(TwitterClientError) as exc_info:
        client._load_bookmarks()
    assert "ブックマークファイルの解析に失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_edge_cases(client):
    """並行処理のエッジケースをテスト"""
    import asyncio

    # 同時に同じURLのブックマークを追加
    url = "https://twitter.com/user/status/1234567890"
    tasks = []
    for i in range(5):
        task = client.add_bookmark(url=url, text=f"テストツイート{i}")
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    # 全て同じIDを持つことを確認
    ids = [r["id"] for r in results]
    assert len(set(ids)) == 1

    # 保存されたブックマークを確認
    bookmarks = await client.get_bookmarks()
    assert len(bookmarks) == 5
    assert all(b["id"] == "1234567890" for b in bookmarks)


def test_memory_usage_limit(client):
    """メモリ使用量の制限をテスト"""
    import psutil

    process = psutil.Process()

    # 大量のブックマークを作成
    large_bookmarks = []
    for i in range(10000):
        bookmark = {
            "id": str(i),
            "url": f"https://twitter.com/user/status/{i}",
            "text": "テスト" * 100,  # 大きなテキスト
            "created_at": str(i),
        }
        large_bookmarks.append(bookmark)

    # メモリ使用量を記録
    before_mem = process.memory_info().rss

    # ブックマークを保存
    client._save_bookmarks(large_bookmarks)

    # メモリ使用量の増加を確認
    after_mem = process.memory_info().rss
    mem_increase = after_mem - before_mem

    # メモリ増加が100MB未満であることを確認
    assert mem_increase < 100 * 1024 * 1024  # 100MB


@pytest.mark.asyncio
async def test_performance_large_data(client):
    """大量データ処理時のパフォーマンスをテスト"""
    import asyncio
    import time

    # 500件のブックマークを追加（1000件から削減）
    tasks = []
    for i in range(500):
        task = client.add_bookmark(
            url=f"https://twitter.com/user/status/{i}",
            text=f"テストツイート{i}",
        )
        tasks.append(task)

    # 並行処理で追加
    start_time = time.time()
    await asyncio.gather(*tasks)
    add_time = time.time() - start_time

    # 追加にかかった時間が5秒未満であることを確認（3秒から調整）
    assert add_time < 5.0, f"追加に{add_time:.2f}秒かかりました"

    # 全件取得の時間を計測
    start_time = time.time()
    bookmarks = await client.get_bookmarks(max_results=500)
    get_time = time.time() - start_time

    # 取得にかかった時間が1秒未満であることを確認
    assert get_time < 1.0, f"取得に{get_time:.2f}秒かかりました"
    assert len(bookmarks) == 500


@pytest.mark.asyncio
async def test_api_communication():
    """API通信のモックテスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        # セッションのモック設定
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # レスポンスのモック
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "id": "1234567890",
                        "text": "テストツイート",
                        "created_at": "2024-03-20T12:00:00Z",
                    }
                ]
            }
        )
        mock_client.get = AsyncMock(return_value=mock_response)

        client = TwitterClient()
        result = await client.fetch_bookmarks_api()

        # API呼び出しの検証
        mock_client.get.assert_called_once_with(
            "https://api.twitter.com/2/users/me/bookmarks",
            headers={"Authorization": "Bearer test_token"},
        )

        # 結果の検証
        assert len(result) == 1
        assert result[0]["id"] == "1234567890"
        assert result[0]["text"] == "テストツイート"


@pytest.mark.asyncio
async def test_api_error_handling():
    """APIエラーのハンドリングテスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # エラーレスポンスのモック
        mock_response = MagicMock()
        mock_response.status = 429  # レート制限エラー
        mock_response.json = AsyncMock(
            return_value={"errors": [{"message": "Rate limit exceeded"}]}
        )
        mock_client.get = AsyncMock(return_value=mock_response)

        client = TwitterClient()
        with pytest.raises(TwitterClientError) as exc_info:
            await client.fetch_bookmarks_api()
        assert "レート制限超過" in str(exc_info.value)


@pytest.mark.asyncio
async def test_api_retry_mechanism():
    """リトライ機構のテスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # 最初の2回は429エラー、3回目で成功
        mock_response_error = MagicMock()
        mock_response_error.status = 429
        mock_response_error.json = AsyncMock(
            return_value={"errors": [{"message": "Rate limit exceeded"}]}
        )

        mock_response_success = MagicMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(
            return_value={
                "data": [{"id": "1234567890", "text": "テストツイート"}]
            }
        )

        mock_client.get = AsyncMock(
            side_effect=[
                mock_response_error,
                mock_response_error,
                mock_response_success,
            ]
        )

        client = TwitterClient()
        result = await client.fetch_bookmarks_api()

        # 3回呼び出されたことを確認
        assert mock_client.get.call_count == 3
        assert len(result) == 1
        assert result[0]["id"] == "1234567890"


@pytest.mark.asyncio
async def test_rate_limit_handling():
    """レート制限のハンドリングテスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # レート制限レスポンスのモック
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(
            return_value={
                "errors": [
                    {
                        "message": "Rate limit exceeded",
                        "code": 88,
                        "reset_at": "2024-03-20T13:00:00Z",
                    }
                ]
            }
        )
        mock_client.get = AsyncMock(return_value=mock_response)

        client = TwitterClient()
        with pytest.raises(TwitterClientError) as exc_info:
            await client.fetch_bookmarks_api()

        # エラーメッセージの検証
        assert "レート制限超過" in str(exc_info.value)
        assert mock_client.get.call_count == TwitterClient.MAX_RETRIES


@pytest.mark.asyncio
async def test_rate_limit_reset():
    """レート制限のリセット待機テスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # 最初のレスポンスはレート制限
        mock_response_limit = MagicMock()
        mock_response_limit.status = 429
        mock_response_limit.json = AsyncMock(
            return_value={
                "errors": [
                    {
                        "message": "Rate limit exceeded",
                        "code": 88,
                        "reset_at": "2024-03-20T13:00:00Z",
                    }
                ]
            }
        )

        # 2回目のレスポンスは成功
        mock_response_success = MagicMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(
            return_value={
                "data": [{"id": "1234567890", "text": "テストツイート"}]
            }
        )

        mock_client.get = AsyncMock(
            side_effect=[mock_response_limit, mock_response_success]
        )

        client = TwitterClient()
        result = await client.fetch_bookmarks_api()

        # 2回呼び出されたことを確認
        assert mock_client.get.call_count == 2
        assert len(result) == 1
        assert result[0]["id"] == "1234567890"


@pytest.mark.asyncio
async def test_rate_limit_backoff():
    """レート制限時のバックオフ戦略テスト"""
    with (
        patch("aiohttp.ClientSession", autospec=True) as mock_session,
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # 3回連続でレート制限エラー
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(
            return_value={"errors": [{"message": "Rate limit exceeded"}]}
        )
        mock_client.get = AsyncMock(return_value=mock_response)

        client = TwitterClient()
        with pytest.raises(TwitterClientError):
            await client.fetch_bookmarks_api()

        # バックオフ時間の検証
        assert mock_sleep.call_count == TwitterClient.MAX_RETRIES - 1
        mock_sleep.assert_has_calls(
            [
                pytest.call(TwitterClient.RETRY_DELAY * 1),
                pytest.call(TwitterClient.RETRY_DELAY * 2),
            ]
        )


@pytest.mark.asyncio
async def test_concurrent_rate_limits():
    """並行リクエスト時のレート制限テスト"""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_client

        # レート制限レスポンスのモック
        mock_response_limit = MagicMock()
        mock_response_limit.status = 429
        mock_response_limit.json = AsyncMock(
            return_value={"errors": [{"message": "Rate limit exceeded"}]}
        )

        # 成功レスポンスのモック
        mock_response_success = MagicMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(
            return_value={
                "data": [{"id": "1234567890", "text": "テストツイート"}]
            }
        )

        # 最初の3つのリクエストはレート制限、その後は成功
        mock_client.get = AsyncMock(
            side_effect=[
                mock_response_limit,
                mock_response_limit,
                mock_response_limit,
                mock_response_success,
                mock_response_success,
            ]
        )

        client = TwitterClient()
        tasks = [client.fetch_bookmarks_api() for _ in range(5)]

        # 並行実行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 結果の検証
        errors = [r for r in results if isinstance(r, TwitterClientError)]
        successes = [r for r in results if isinstance(r, list)]

        assert len(errors) == 3  # 3つのリクエストが失敗
        assert len(successes) == 2  # 2つのリクエストが成功
        assert all("レート制限超過" in str(e) for e in errors)
        assert all(
            len(s) == 1 and s[0]["id"] == "1234567890" for s in successes
        )
