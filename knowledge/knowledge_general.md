# LLM Knowledge Management

## 基本方針
- このファイルは、LLMの知識の限界と更新に関する記録を管理します
- LLMは自身の知識カットオフ日付を認識し、それ以降の情報については特に慎重に扱います

## 知識の確認と更新プロセス

### 1. 知識の確認が必要なケース
- LLMの知識カットオフ日以降に関する技術情報
- ライブラリやフレームワークのバージョン依存の情報
- 新しい技術標準や仕様に関する情報

### 2. 確認方法
- 公式ドキュメントの参照
- ソースコードの直接確認
- パッケージのリリースノートの確認

### 3. 記録すべき情報
```date: YYYY-MM-DD```形式で日付を記録し、以下を含めます：
- 確認した事実
- 情報源（URL、コミットハッシュなど）
- LLMの既存知識との差分
- 影響を受ける機能や実装範囲

## 確認済み知識ログ

### ライブラリ・フレームワーク

```
[YYYY-MM-DD] ライブラリ名/フレームワーク名
- 確認内容：
- 情報源：
- 既存知識との差分：
- 影響範囲：

```

### 言語仕様・標準

```
[YYYY-MM-DD] 言語/標準名
- 確認内容：
- 情報源：
- 既存知識との差分：
- 影響範囲：

```

### API・サービス

```
[YYYY-MM-DD] API/サービス名
- 確認内容：
- 情報源：
- 既存知識との差分：
- 影響範囲：
```

# 一般的な知見

## 環境変数による設定パターン

### 基本原則
1. デフォルト値の提供
```python
value = os.getenv("KEY", "default_value")
```
- 後方互換性の維持
- 明示的なデフォルト値
- 設定忘れ防止

2. 設定の階層化
- 必須設定: 未設定時にエラー
- オプション設定: デフォルト値を提供
- 開発設定: 開発環境のみで使用

### ベストプラクティス
1. URL設定
```python
# 良い例
host = os.getenv("API_HOST", "https://api.example.com")
endpoint = f"{host}/v1/endpoint"

# 避けるべき例
protocol = os.getenv("API_PROTOCOL", "https")
domain = os.getenv("API_DOMAIN", "api.example.com")
endpoint = f"{protocol}://{domain}/v1/endpoint"
```
- 完全なURLをデフォルト値として提供
- URLの分割は避ける
- プロトコルを含めた設定

2. 設定の検証
```python
def validate_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))

host = os.getenv("API_HOST", "https://api.example.com")
if not validate_url(host):
    raise ValueError("Invalid URL format")
```
- 形式の検証
- セキュリティ考慮（HTTPS推奨）
- エラーメッセージの明確化

### 実装例
1. Difyホスト設定
```python
# 設定例
self.dify_host = os.getenv("DIFY_HOST", "https://api.dify.ai")

# 使用例
endpoint = f"{self.dify_host}/v1/completion-messages"
```
- 完全なURLを使用
- デフォルト値の提供
- エンドポイントの動的構築

### テストパターン

## 非同期テスト設定

### pytest.ini の設定
```ini
[pytest]
asyncio_mode = strict
asyncio_default_fixture_loop_scope = function

filterwarnings =
    ignore::RuntimeWarning:app.query_monitor
    ignore::DeprecationWarning:pytest_asyncio.plugin
```

### イベントループの設定
```python
@pytest.fixture(scope="session")
def event_loop_policy():
    """イベントループポリシーの設定"""
    return asyncio.get_event_loop_policy()
```

### 非同期モックの設定
```python
@pytest.fixture
def mock_response():
    """APIレスポンスのモック"""
    mock = AsyncMock()
    mock.status = 200
    mock.json.return_value = {"answer": "テスト結果"}
    return mock

@pytest.fixture
def mock_session(mock_response):
    """セッションのモック"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_response
    cm.__aexit__.return_value = None
    session.post.return_value = cm
    return session
```

### テストケースの実装
```python
@pytest.mark.asyncio
async def test_async_function():
    """非同期関数のテスト"""
    # Given
    mock_response = AsyncMock()
    mock_response.json.return_value = {"result": "success"}
    
    # When
    async with mock_response as response:
        result = await response.json()
    
    # Then
    assert result == {"result": "success"}
    mock_response.__aenter__.assert_called_once()
    mock_response.__aexit__.assert_called_once()
```

## テストカバレッジ管理

### カバレッジ設定
```ini
[pytest]
addopts = --cov=app --cov-report=term-missing
```

### カバレッジ目標
- 最低限: 80%
- 目標: 90%以上
- 重要なモジュール: 95%以上

### カバレッジレポートの読み方
```
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
app/module.py           100    10     90%    45-50,60-65
```
- Stmts: 総行数
- Miss: カバーされていない行数
- Cover: カバレッジ率
- Missing: カバーされていない行番号

### カバレッジ改善戦略
1. 未カバー行の特定
2. テストケースの追加
3. エッジケースのテスト
4. 例外パスのテスト

# API利用パターン

## Dify API
1. エンドポイント選択
```python
# チャットメッセージ用
endpoint = f"{host}/v1/chat-messages"

# レスポンスモード
response_mode = "blocking"  # または "streaming"
```

2. リクエスト構造
```python
payload = {
    "inputs": {},
    "query": "クエリ文字列",
    "response_mode": "blocking",
    "conversation_id": "",
    "user": "user_id"
}
```

3. 認証
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

4. エラーハンドリング
```python
if response.status != 200:
    error_text = await response.text()
    raise APIError(f"Status: {response.status}, Error: {error_text}")
```