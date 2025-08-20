# AMS テストガイド

## テスト実行方法

### 現在の問題点
単体テストに `@pytest.mark.unit` マーカーが付いていないため、以下のコマンドは期待通りに動作しません：
```bash
pytest -m "unit"  # 0件のテストが実行される
```

### 推奨される実行方法

#### 1. 単体テストのみ実行（APIキー不要）
```bash
# tests/unit/ディレクトリのテストを実行
pytest tests/unit/

# 特定の単体テストを実行
pytest tests/unit/test_llm_transparency.py -v
```

#### 2. 統合テストを除外して実行
```bash
# 統合テスト以外を実行（単体テストのみ）
pytest -m "not integration"

# より明示的に
pytest tests/unit/ -v
```

#### 3. 統合テストのみ実行（有効なAPIキー必要）
```bash
# 統合テストマーカーが付いたテストのみ
pytest -m "integration"

# または直接ディレクトリ指定
pytest tests/integration/
```

#### 4. すべてのテスト実行
```bash
# 全テスト実行（APIキーが必要）
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html
```

## テスト分類

### 単体テスト（tests/unit/）
- **APIキー不要**: モックは原則禁止（外部I/O・LLM呼び出し等の境界のみ、事前承認がある場合に限る）
- **高速実行**: 外部API呼び出しなし（境界はスタブ/フェイク等で代替）
- **対象**: 個別コンポーネントのロジック

### 統合テスト（tests/integration/）
- **APIキー必要**: 実際のLLM APIを呼び出し
- **実行時間**: 長め（ネットワーク通信あり）
- **対象**: コンポーネント間の連携

## エラー時の対処

### APIキーエラーの場合
```
API key expired. Please renew the API key.
```

対処法：
1. 有効なGoogle APIキーを取得
2. `/home/devuser/workspace/app/ams/.env` に設定
3. 単体テストのみ実行: `pytest tests/unit/`

### 環境変数エラーの場合
```bash
# 環境変数の確認
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
```

## 推奨ワークフロー

### 開発時
```bash
# 1. 単体テストを頻繁に実行
pytest tests/unit/ -v

# 2. 変更したファイルのテストのみ
pytest tests/unit/test_analyzer.py::TestAnalysisAgent -v

# 3. 統合テストは必要時のみ
pytest tests/integration/test_llm_connection.py::test_basic_llm_connection -v
```

### CI/CD前
```bash
# 1. 単体テストの確認
pytest tests/unit/

# 2. カバレッジ確認
pytest tests/unit/ --cov=src --cov-report=term-missing

# 3. 統合テスト（APIキーがある場合）
pytest -m "integration"
```

## 今後の改善案

1. **単体テストにマーカー追加**
   ```python
   @pytest.mark.unit
   @pytest.mark.asyncio
   async def test_example():
       pass
   ```

2. **conftest.pyでの自動マーカー設定**
   ```python
   # tests/unit/conftest.py
   import pytest

   def pytest_collection_modifyitems(items):
       for item in items:
           if "unit" in str(item.fspath):
               item.add_marker(pytest.mark.unit)
   ```

3. **環境別設定**
   ```bash
   # .env.test
  # TEST_MODE は廃止（実APIキー必須）
   MOCK_LLM=true
   ```