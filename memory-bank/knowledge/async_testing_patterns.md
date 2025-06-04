# 非同期テスト パターン

`techContext.md` (旧版) より抽出した `pytest-asyncio` を利用した非同期テストに関するパターンと知見。

## テストフレームワーク構成

*   **メイン:** pytest
*   **非同期サポート:** pytest-asyncio
*   **カバレッジ:** pytest-cov

## テスト設定例 (`pytest.ini`)

```ini
[pytest]
asyncio_mode = strict
# テスト関数ごとに独立したイベントループを使用する設定 (推奨)
asyncio_default_fixture_loop_scope = function
# カバレッジ測定対象とレポート形式の指定例
addopts = --cov=app --cov-report=term-missing
# 特定の警告を無視する設定例 (状況に応じて調整)
filterwarnings =
    ignore::RuntimeWarning:app.query_monitor # 例: 特定モジュールのRuntimeWarningを無視
```

## 主要なテストパターン

### 非同期コンテキストマネージャのモック

`aiohttp.ClientSession` のような非同期コンテキストマネージャをモック化する例。

```python
import pytest_asyncio
from unittest.mock import AsyncMock
import aiohttp

@pytest_asyncio.fixture
async def mock_session():
    # aiohttp.ClientSessionを模倣するAsyncMockを作成
    session = AsyncMock(spec=aiohttp.ClientSession)
    # __aenter__が返すモック(レスポンスオブジェクト相当)を作成
    response_mock = AsyncMock()
    response_mock.status = 200
    async def json_func(): # 非同期メソッドを模倣
        return {"key": "value"}
    response_mock.json = json_func
    # コンテキストマネージャのモックを作成
    cm_mock = AsyncMock()
    cm_mock.__aenter__.return_value = response_mock # __aenter__がレスポンスモックを返す
    cm_mock.__aexit__.return_value = None # __aexit__は通常Noneを返す
    # session.post()などがコンテキストマネージャモックを返すように設定
    session.post.return_value = cm_mock
    return session

# 利用例
@pytest.mark.asyncio
async def test_api_call(mock_session):
    async with mock_session.post("http://example.com") as response:
        assert response.status == 200
        data = await response.json()
        assert data["key"] == "value"
    # 呼び出しのアサーションなど
    mock_session.post.assert_called_once()

```

### イベントループ管理 (`event_loop_policy` フィクスチャ)

`pytest-asyncio` では、関数スコープのイベントループがデフォルトで提供されます。カスタムの `event_loop` フィクスチャは非推奨であり、通常は不要です。ポリシーレベルでの設定が必要な場合に `event_loop_policy` を使用することがあります（多くの場合不要）。

```python
import pytest
import asyncio

# 通常は pytest.ini で asyncio_default_fixture_loop_scope = function を設定すれば十分
# ポリシーレベルでの操作が必要な稀なケースでのみ使用を検討
@pytest.fixture(scope="session")
def event_loop_policy():
    # 例: 特定のポリシーを強制する場合など (通常は不要)
    # return asyncio.WindowsSelectorEventLoopPolicy() # Windowsの例
    return asyncio.get_event_loop_policy()
```

## ベストプラクティス

1.  **イベントループ設定:**
    *   `pytest.ini` で `asyncio_default_fixture_loop_scope = function` を設定し、テスト間の分離を確保する。
    *   カスタムの `event_loop` フィクスチャの使用は避ける。
2.  **非同期モック設定:**
    *   非同期コンテキストマネージャには `unittest.mock.AsyncMock` を使用する。
    *   `__aenter__` と `__aexit__` の戻り値を明示的に設定する。
    *   非同期メソッドのモックには `async def` または `AsyncMock(return_value=...)` を使用する。
3.  **エラーハンドリングテスト:**
    *   正常系だけでなく、異常系のパスもテストする。
    *   例外が適切に送出・処理されることを確認する。
    *   エラー通知などの副作用も検証する。
4.  **警告管理:**
    *   `pytest.ini` の `filterwarnings` で意図しない警告を抑制する。
    *   テスト実行時に発生する警告（特に `RuntimeWarning`）の原因を調査し、適切に対処する。

## 既知の問題と解決策（例）

### 非同期コンテキストマネージャ関連

1.  **問題:** `AttributeError: __aenter__` / `AttributeError: __aexit__`
    **原因:** モックオブジェクトに `__aenter__` や `__aexit__` が正しく設定されていない。
    **解決策:** 上記「非同期コンテキストマネージャのモック」の例のように、`AsyncMock` を使用して `__aenter__` と `__aexit__` を設定する。
2.  **問題:** モックが複数回呼び出された際の引数や順序の検証が難しい。
    **解決策:** `mock_object.call_args_list` を使用して、各呼び出しの引数をリストとして取得し、検証する。`mock_object.assert_has_calls([...])` なども利用可能。

### イベントループ関連

1.  **問題:** `DeprecationWarning: The event_loop fixture is deprecated`
    **解決策:** テストコードから `event_loop` フィクスチャへの依存を削除する。`pytest-asyncio` が適切なスコープでループを提供する。
2.  **問題:** テスト間で状態が共有されてしまう。
    **解決策:** `pytest.ini` で `asyncio_default_fixture_loop_scope = function` を設定する。

## 依存関係（例）

*   pytest-asyncio: ^0.2x.x
*   pytest: ^8.x.x
*   pytest-cov: ^x.x.x

**(注意: 上記バージョンは旧 `techContext.md` に記載されていた例であり、実際のプロジェクトに合わせて更新が必要です)** 