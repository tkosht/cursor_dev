# テスト戦略

## 基本方針
*   [project.mdc](mdc:.cursor/rules/project.mdc) の指示に従い、**テスト駆動開発 (TDD)** を原則とする。
*   テストは仕様として扱い、実装前にテストケースを検討・作成する。
*   [python.mdc](mdc:.cursor/rules/python.mdc) の指示に従い、`tests/` ディレクトリにテストコードを配置し、`pytest` を使用する。

## テストの種類と目的
*   **単体テスト (Unit Test):**
    *   目的: 個々の関数、メソッド、クラスが期待通りに動作することを確認する。
    *   対象: `app/` 内の各モジュール。
    *   ツール: `pytest`, `unittest.mock` (必要に応じて)
*   **結合テスト (Integration Test):**
    *   目的: 複数のコンポーネントが連携して正しく機能することを確認する。
    *   対象: モジュール間連携、外部API連携など。
    *   ツール: `pytest`
*   **(必要に応じて) E2Eテスト (End-to-End Test):**
    *   目的: システム全体がユーザーシナリオ通りに動作することを確認する。
    *   ツール: (プロジェクトに応じて選定、例: Selenium, Playwright)

## テストカバレッジ
*   目標カバレッジ: (プロジェクトとして目標値を設定する場合は記述。例: 80%以上)
*   測定ツール: `pytest-cov`

## テスト実行
*   [development.mdc](mdc:.cursor/rules/development.mdc) の開発工程に従い、実装後およびコードレビュー後に実行する。
*   CI/CD パイプラインでの自動実行を推奨。

## テスト失敗時の対応
*   [error_analysis.md](mdc:memory-bank/error_analysis.md) のプロセスに従い、原因を特定し修正する。

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

### カバレッジ状況 (現状)
```
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
app/query_monitor.py     160     19    88%   181-183 245-246 273-277 330-335 367-369 394-396 400
----------------------------------------------------
TOTAL                    160     19    88%
```

- テスト件数：32件
- カバレッジ：88%
- 未カバー：主にエラー処理や新追加関数の一部

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

### TDD原則の徹底
- テストを先に書き、テストが失敗することを確認してから実装する
- テストケースは仕様書であり、コードの動作を定義するもの
- テストケースの期待値を実装に合わせて変更するのではなく、実装をテストの期待値に合わせる
- テストケースの修正が必要な場合は、以下のプロセスに従う：
  1. テストケースの妥当性を評価（コア機能の意図を反映しているか）
  2. 必要に応じてテストケースを修正（修正理由を明記）
  3. 修正したテストケースに合わせてコードを実装
  4. テストが通ることを確認

#### テストケース修正のガイドライン
```
# テストケース修正チェックリスト
1. このテストは何を検証すべきか？（テストの目的）
2. 現在のテストケースは正しい仕様を反映しているか？
3. 修正が必要な場合、どのような修正が適切か？
4. なぜその修正が必要なのか？（根拠）
5. 修正後のテストケースは元の検証目的を満たしているか？
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

## 非同期テスト戦略

### イベントループ管理
```python
@pytest.fixture(scope="function")
def event_loop():
    """Create and cleanup event loop for each test"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
```

### モックの実装
```python
@pytest_asyncio.fixture
async def mock_session(mock_response):
    """セッションのモック"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cm = AsyncMock()
    cm.__aenter__.return_value = mock_response
    cm.__aexit__.return_value = None
    session.post.return_value = cm
    session.closed = False
    return session
```

### テストケース設計
1. 正常系テスト
   - 基本的な機能の確認
   - 期待される結果の検証
   - 境界値のテスト

2. 異常系テスト
   - エラー発生時の挙動確認
   - リトライロジックの検証
   - タイムアウト処理の確認

3. エッジケース
   - 空の結果の処理
   - 無効なJSONレスポンス
   - 接続エラーの処理
