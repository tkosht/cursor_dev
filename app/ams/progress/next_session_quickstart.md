# AMS プロジェクト - 次回セッション クイックスタートガイド

## 🚀 セッション開始手順

### 1. プロジェクトディレクトリへ移動
```bash
cd /home/devuser/workspace/app/ams
```

### 2. 進捗確認
```bash
cat progress/session_20250803_progress.md
```

### 3. 現在のブランチ確認
```bash
git branch --show-current
git status
```

### 4. 最新の変更を取得
```bash
git checkout main
git pull origin main
```

## 📋 推奨タスク（優先順位順）

### 1. 境界値テストの追加（推定: 2時間）
```bash
# 新しいブランチを作成
git checkout -b task/add-boundary-tests

# テストファイルを編集
code tests/unit/test_aggregator.py
code tests/unit/test_reporter.py

# テスト実行
poetry run pytest tests/unit/test_aggregator.py -v
poetry run pytest tests/unit/test_reporter.py -v
```

### 2. パフォーマンステストの実装（推定: 4時間）
```bash
# パフォーマンステスト用ディレクトリ作成
mkdir -p tests/performance

# ベンチマークテスト作成
code tests/performance/test_aggregator_performance.py
code tests/performance/test_reporter_performance.py

# 必要なパッケージ追加
poetry add --group dev pytest-benchmark
```

### 3. E2Eテストの実装（推定: 6時間）
```bash
# E2Eテスト用ディレクトリ作成
mkdir -p tests/e2e

# E2Eテスト作成
code tests/e2e/test_full_simulation_flow.py
```

## 🔧 開発環境セットアップ

### 仮想環境の有効化
```bash
poetry shell
```

### 依存関係の確認
```bash
poetry install
```

### テスト実行コマンド
```bash
# 単体テスト
poetry run pytest tests/unit/ -v

# 統合テスト
poetry run pytest tests/integration/ -v

# カバレッジ付き
poetry run pytest --cov=src.agents --cov-report=term-missing
```

### コード品質チェック
```bash
# フォーマット
poetry run black src/ tests/

# リント
poetry run ruff check src/ tests/

# 型チェック（注意: 現在エラーあり）
poetry run mypy src/ --ignore-missing-imports
```

## 📍 重要ファイルのクイックアクセス

### 実装ファイル
- AggregatorAgent: `src/agents/aggregator.py`
- ReporterAgent: `src/agents/reporter.py`
- OrchestratorAgent: `src/agents/orchestrator.py`

### テストファイル
- 単体テスト: `tests/unit/test_aggregator.py`, `tests/unit/test_reporter.py`
- 統合テスト: `tests/integration/test_orchestrator_integration.py`

### ドキュメント
- 実装サマリー: `checklists/aggregator_reporter_implementation_summary.md`
- 改善提案: `checklists/improvement_recommendations.md`
- レビュー結果: `checklists/test_review_results.md`

## 🌟 ヒント

1. **Serenaメモリ確認**
```
mcp__serena__read_memory ams_project_aggregator_reporter_implementation
```

2. **Cogneeステータス確認**
```
mcp__cognee__cognify_status
```

3. **最新のPR確認**
- PR #68: https://github.com/tkosht/cursor_dev/pull/68
- PR #69: https://github.com/tkosht/cursor_dev/pull/69

---

準備完了！上記の手順に従って、前回の続きから開発を再開できます。