# テスト戦略

## 1. 基本原則
### 絶対禁止（MUST NOT）
- 本番コードにテストライブラリをインポートしない
- 本番コードにテスト用の分岐を入れない
- テスト済コードの変更（例外：セキュリティ/重大バグ/重大パフォーマンス問題）

### 必須要件（MUST）
- 新機能は新しいクラス/関数として実装
- 既存機能の再利用は委譲パターンで実装
- 非同期テストは`@pytest_asyncio.fixture`を使用
- 非同期モックは完全実装する

## 2. テスト構造
### カバレッジ要件
- 単体テスト：90%以上（全体の60%）
- 統合テスト：70%以上（全体の30%）
- E2Eテスト：主要フロー100%（全体の10%）

### 優先順位
- P0（100%）：セキュリティ、データ整合性、決済、認証
- P1（90%）：ビジネスロジック、バリデーション
- P2（70%）：ユーティリティ、UI表示

## 3. 品質保証
### 自動チェック
- コミット時：単体テスト
- PRレビュー時：単体＋統合テスト
- マージ時：全テスト
- 定期実行：日次全テスト、週次性能テスト

### レビュー基準
- コードレビュー（最低3名）
- アーキテクト承認
- QA承認
- セキュリティ承認（必要時）

## 4. 実装規約
### テストコード構造
```python
def test_機能名_条件_期待結果():
    # Given（準備）
    # When（実行）
    # Then（検証）
```

### モック使用基準
- 外部依存がある場合
- 実行時間が長い処理
- 非決定的な処理
- 非同期コンテキストマネージャーの場合
  - AsyncMockを使用
  - __aenter__と__aexit__を適切に実装
  - コンテキストマネージャーの戻り値を設定

### 非同期テストパターン
```python
@pytest_asyncio.fixture
async def mock_async_context():
    """非同期コンテキストマネージャーのモック"""
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock

@pytest.mark.asyncio
async def test_async_operation(mock_async_context):
    """非同期操作のテスト"""
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

## 5. 監視と改善
### メトリクス
- テストカバレッジ（行/分岐）
- テスト成功率
- テスト実行時間
- 非同期テストの安定性

### 定期メンテナンス
- テストの有効性確認
- 不要なテストの削除
- 実行時間の最適化
- 非同期テストパターンの更新
