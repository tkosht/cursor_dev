# A2Aプロトコル実装ルール

## 🎯 A2Aプロトコルの核心

### 基本原則

1. **エージェントの自律性**: 各エージェントは独立して動作可能
2. **相互運用性**: 標準化されたメッセージフォーマット
3. **発見可能性**: エージェントの能力を動的に確認可能
4. **拡張性**: 新しいエージェントの追加が容易

## 📋 必須実装要素

### 1. エージェントカード

**必須フィールド**:
```python
{
    "name": str,           # エージェント名
    "version": str,        # バージョン（semver形式）
    "description": str,    # 簡潔な説明
    "skills": List[Skill], # 実行可能なスキル一覧
}
```

**スキル定義**:
```python
{
    "id": str,              # スキルの一意識別子
    "name": str,            # 人間が読める名前
    "description": str,     # スキルの説明
    "tags": List[str],      # 検索用タグ
    "examples": List[str],  # 使用例
}
```

### 2. メッセージフォーマット

**リクエスト形式**:
```python
{
    "action": str,          # 実行するアクション
    "data": Optional[Dict], # アクションに必要なデータ
    "context": Optional[Dict], # 追加のコンテキスト情報
}
```

**レスポンス形式**:
```python
{
    "success": bool,        # 成功/失敗
    "data": Optional[Dict], # 結果データ
    "error": Optional[str], # エラーメッセージ
    "metadata": Optional[Dict], # メタ情報
}
```

### 3. エラーハンドリング

**標準エラーコード**:
- `400`: 無効なリクエスト
- `404`: リソースが見つからない
- `429`: レート制限超過
- `500`: 内部エラー

**エラーレスポンス**:
```python
{
    "success": false,
    "error": "Human readable error message",
    "error_code": "SPECIFIC_ERROR_CODE",
    "details": {} # デバッグ用詳細（本番では最小限）
}
```

## 🏗️ 実装アーキテクチャ

### 推奨層構造

```
1. Protocol Layer（プロトコル層）
   - メッセージの検証・変換
   - プロトコル準拠の保証

2. Agent Layer（エージェント層）
   - エージェントカードの管理
   - メッセージルーティング

3. Skill Layer（スキル層）
   - ビジネスロジックの実装
   - スキルの登録・実行

4. Storage Layer（永続化層）
   - 状態の保存・復元
   - トランザクション管理
```

### インターフェース設計

```python
class A2AAgent(ABC):
    @abstractmethod
    def get_agent_card(self) -> AgentCard:
        """エージェントカードを返す"""
        pass
    
    @abstractmethod
    def handle_message(self, message: Dict) -> Dict:
        """A2Aメッセージを処理"""
        pass
    
    @abstractmethod
    def discover_skills(self) -> List[Skill]:
        """利用可能なスキルを発見"""
        pass
```

## 🔐 セキュリティ要件

### 1. 認証・認可

**必須実装**:
- エージェント間の相互認証
- メッセージ署名の検証
- アクセス権限の管理

**実装例**:
```python
def verify_message(message: Dict, signature: str) -> bool:
    """メッセージの署名を検証"""
    expected = hmac.new(
        secret_key.encode(),
        json.dumps(message).encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### 2. データ保護

**暗号化要件**:
- 機密データの暗号化（AES-256）
- 通信路の暗号化（TLS 1.3）
- キー管理の実装

### 3. 監査ログ

**必須記録項目**:
- リクエスト元
- 実行アクション
- タイムスタンプ
- 結果（成功/失敗）
- エラー詳細（該当する場合）

## 🚀 パフォーマンス基準

### レスポンスタイム目標

| 操作 | 目標時間 | 最大許容時間 |
|------|---------|-------------|
| エージェントカード取得 | 10ms | 50ms |
| 単純なアクション | 50ms | 200ms |
| 複雑なアクション | 200ms | 1000ms |
| バッチ処理 | 1s | 5s |

### スケーラビリティ要件

- 同時接続数: 最小1000
- スループット: 1000 req/s
- レイテンシ: p99 < 100ms

## 📝 実装チェックリスト

### 基本機能

- [ ] エージェントカードの実装
- [ ] メッセージハンドリング
- [ ] スキル登録機能
- [ ] エラーハンドリング
- [ ] ロギング実装

### セキュリティ

- [ ] 入力検証
- [ ] 認証機能
- [ ] レート制限
- [ ] 監査ログ
- [ ] エラー情報の制限

### 品質保証

- [ ] ユニットテスト（カバレッジ85%以上）
- [ ] 統合テスト
- [ ] パフォーマンステスト
- [ ] セキュリティテスト
- [ ] ドキュメント整備

### 運用準備

- [ ] モニタリング設定
- [ ] アラート設定
- [ ] バックアップ戦略
- [ ] 障害復旧手順
- [ ] スケーリング戦略

## 🔄 バージョニング

### セマンティックバージョニング

```
MAJOR.MINOR.PATCH

MAJOR: 後方互換性のない変更
MINOR: 後方互換性のある機能追加
PATCH: 後方互換性のあるバグ修正
```

### APIバージョン管理

**URLパス方式**:
```
/v1/agent/message
/v2/agent/message
```

**ヘッダー方式**:
```
A2A-Version: 1.0
```

## 🌐 相互運用性

### 他プロトコルとの連携

**サポートすべき形式**:
- REST API
- GraphQL
- WebSocket
- gRPC

### データフォーマット

**必須サポート**:
- JSON（デフォルト）
- MessagePack（バイナリ）
- Protocol Buffers（高性能）

## 📚 ベストプラクティス

### 1. 非同期処理

```python
async def handle_message_async(self, message: Dict) -> Dict:
    """非同期メッセージ処理"""
    try:
        result = await self._process_async(message)
        return {"success": True, "data": result}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout"}
```

### 2. 回復力のある設計

- サーキットブレーカーパターン
- リトライ with exponential backoff
- フォールバック機構
- グレースフルデグラデーション

### 3. 観測可能性

- 分散トレーシング（OpenTelemetry）
- メトリクス収集（Prometheus）
- 構造化ログ（JSON形式）
- ヘルスチェックエンドポイント

## 🚨 アンチパターン

### 避けるべき実装

1. **同期的なブロッキング処理**
2. **グローバル状態の使用**
3. **エラーの握りつぶし**
4. **無制限のリソース使用**
5. **ハードコードされた設定**

### よくある間違い

1. **エージェントカードの静的定義**
   - ❌ ハードコードされたスキル一覧
   - ✅ 動的に発見可能なスキル

2. **エラー情報の過剰露出**
   - ❌ スタックトレースをクライアントに返す
   - ✅ 一般的なエラーメッセージ

3. **状態の不適切な管理**
   - ❌ メモリ内のみの状態保持
   - ✅ 永続化層での適切な管理

---

*このルールは、A2Aプロトコルの実装において遵守すべき基準を定めています。プロジェクトの進化に応じて継続的に更新してください。*