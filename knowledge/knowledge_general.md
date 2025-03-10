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
1. カスタム設定のテスト
```python
with patch.dict(os.environ, {"API_HOST": "https://custom.example.com"}):
    client = APIClient()
    assert client.host == "https://custom.example.com"
```

2. デフォルト値のテスト
```python
with patch.dict(os.environ, {}, clear=True):
    client = APIClient()
    assert client.host == "https://api.example.com"
```

3. 非同期テストのパターン
```python
# 非同期コンテキストマネージャーのモック
@pytest_asyncio.fixture
async def mock_async_context():
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock

# 非同期操作のテスト
@pytest.mark.asyncio
async def test_async_operation(mock_async_context):
    # Given（準備）
    mock_async_context.json.return_value = {"result": "success"}
    
    # When（実行）
    async with mock_async_context as ctx:
        result = await ctx.json()
    
    # Then（検証）
    assert result == {"result": "success"}
    mock_async_context.__aenter__.assert_called_once()
    mock_async_context.__aexit__.assert_called_once()
```

### 非同期テストのベストプラクティス
1. モックの設定
- AsyncMockを使用
- コンテキストマネージャーメソッドの実装
- 戻り値の適切な設定

2. テストの構造
- Given-When-Thenパターンの使用
- 非同期コンテキストの適切な処理
- アサーションの明確化

3. エラーハンドリング
- 例外の適切なモック
- エラーケースのテスト
- エラーメッセージの検証

### 注意点
1. セキュリティ
- HTTPS使用の推奨
- 認証情報の分離
- URLエスケープ処理

2. 可用性
- デフォルト値の適切な選択
- エラー処理の実装
- ログ記録の充実

3. メンテナンス性
- 設定の一元管理
- ドキュメントの更新
- テストカバレッジの維持

4. 非同期テスト
- イベントループの適切な管理
- 非同期コンテキストの正しい実装
- テストの安定性確保