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