# テストエラー根本原因分析

## 発見した事実

### 1. RuntimeErrorの詳細
- **エラーメッセージ**: `RuntimeError: Event loop is closed`
- **発生場所**: `/usr/lib/python3.10/asyncio/base_events.py:515`
- **関連警告**: `coroutine 'InterceptedUnaryUnaryCall._invoke' was never awaited`

### 2. テストの挙動パターン
- **個別実行**: 成功
  - test_llm_with_japanese: PASSED (3.38秒)
  - test_multiple_llm_calls: PASSED (20.46秒)
- **全体実行**: 失敗
  - 両テストでRuntimeError発生

### 3. 根本原因
非同期処理とイベントループの競合状態が発生している：

1. **イベントループの早期クローズ**
   - あるテストが終了時にイベントループを閉じる
   - 次のテストがまだ非同期処理を実行中
   - gRPC/Google APIの非同期呼び出しが未完了

2. **coroutineの未await問題**
   - Google APIクライアント（grpc）の非同期呼び出しが適切にawaitされていない
   - テスト終了時にクリーンアップが不完全

## 解決策

### 1. テストフィクスチャの改善
```python
@pytest.fixture(scope="function")
async def clean_event_loop():
    """各テストで新しいイベントループを確保"""
    # テスト前のセットアップ
    yield
    # 非同期タスクの完了を待つ
    await asyncio.sleep(0.1)
```

### 2. 非同期処理の適切な完了待機
```python
async def test_llm_with_japanese():
    llm = create_llm()
    response = await llm.ainvoke("...")
    # 明示的に待機
    await asyncio.sleep(0)  # イベントループに制御を戻す
```

### 3. pytest-asyncioの設定調整
`pyproject.toml`の設定を確認：
- `asyncio-mode = "auto"` が適切に動作しているか
- イベントループのスコープ設定

## 追加調査が必要な項目

1. **test_minimal_pipelineのJSONパースエラー**
   - タイムアウトが発生（2分以上）
   - parse_llm_json_responseでのエラー
   - 大量のAPI呼び出しが原因の可能性

2. **並列実行の設定**
   - pytestの並列実行設定
   - 各テストの独立性確保

## 推奨アクション

1. **短期的対策**
   - 統合テストを逐次実行に変更
   - 各テスト後に明示的なクリーンアップ

2. **長期的対策**
   - 非同期処理の完全な管理
   - テストの独立性向上
   - タイムアウト値の適切な設定