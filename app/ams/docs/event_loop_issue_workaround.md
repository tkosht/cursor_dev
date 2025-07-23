# Event Loop Issue Workaround

## 問題の詳細

Google Generative AI (Gemini) APIのgRPCクライアントとpytest-asyncioの相互作用により、統合テストの一括実行時にイベントループエラーが発生する。

### エラー内容
```
RuntimeError: Event loop is closed
coroutine 'InterceptedUnaryUnaryCall._invoke' was never awaited
AttributeError: 'InterceptedUnaryUnaryCall' object has no attribute '_interceptors_task'
```

### 根本原因
- Google APIのgRPCクライアントが非同期処理を適切に終了しない
- pytest-asyncioとの相性問題
- 個別実行では成功、一括実行では失敗

## 一時的な回避策

### 1. pytestマーカーの追加

```python
# tests/integration/test_llm_connection.py
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.xfail(
    condition=not os.getenv("PYTEST_INDIVIDUAL_RUN"),
    reason="Known issue with event loop in batch execution"
)
async def test_llm_with_japanese():
    ...

@pytest.mark.xfail(
    condition=not os.getenv("PYTEST_INDIVIDUAL_RUN"), 
    reason="Known issue with event loop in batch execution"
)
async def test_multiple_llm_calls():
    ...
```

### 2. テスト実行方法

```bash
# 単体テスト（安定）
pytest tests/unit/ -v

# 統合テスト（問題のあるテストを除外）
pytest tests/integration/ -v -k "not (test_llm_with_japanese or test_multiple_llm_calls)"

# 個別実行（成功）
PYTEST_INDIVIDUAL_RUN=1 pytest tests/integration/test_llm_connection.py::test_llm_with_japanese -v
PYTEST_INDIVIDUAL_RUN=1 pytest tests/integration/test_llm_connection.py::test_multiple_llm_calls -v
```

### 3. CI/CDでの対応

```yaml
# .github/workflows/test.yml
- name: Run Unit Tests
  run: pytest tests/unit/ -v

- name: Run Integration Tests (Stable)
  run: pytest tests/integration/ -v -k "not (test_llm_with_japanese or test_multiple_llm_calls)"

- name: Run Problematic Tests Individually
  run: |
    PYTEST_INDIVIDUAL_RUN=1 pytest tests/integration/test_llm_connection.py::test_llm_with_japanese -v
    PYTEST_INDIVIDUAL_RUN=1 pytest tests/integration/test_llm_connection.py::test_multiple_llm_calls -v
```

## 恒久的な解決策（将来実装予定）

1. **Google APIクライアントの更新待機**
   - langchain-google-genaiの更新を監視
   - gRPCライブラリの修正を待つ

2. **カスタムイベントループ管理**
   - Google API専用のイベントループマネージャー実装
   - gRPCのクリーンアップを強制

3. **別プロセスでの実行**
   - 問題のあるテストを別プロセスで実行
   - multiprocessingを使用した隔離

## 現在のテスト成功率

- **全体**: 104/107 (97.2%)
- **単体テスト**: 88/88 (100%)
- **統合テスト（個別実行）**: 5/5 (100%)
- **統合テスト（一括実行）**: 3/5 (60%)