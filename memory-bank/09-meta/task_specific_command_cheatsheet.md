# タスク別コマンドチートシート

## KEYWORDS: task-commands, cheatsheet, workflow-specific, development-tasks, ai-agent-efficiency
## DOMAIN: meta-knowledge|task-management|daily-operations
## PRIORITY: HIGH
## WHEN: 特定タスク実行時、手順確認時、新しいタスクタイプ
## NAVIGATION: CLAUDE.md → smart_knowledge_load() → task-specific operations → this file

---

## 🆕 新機能開発 (Feature Development)

### 📋 事前準備
```bash
# 1. ブランチ作成・知識ロード
git checkout -b feature/[function-name]
smart_knowledge_load "development" "new-feature"

# 2. 関連知識確認
find memory-bank/ -name "*development*.md" -o -name "*patterns*.md" | head -5
mcp__cognee__search "feature implementation patterns" RAG_COMPLETION
```

### 🔄 TDD開発サイクル
```bash
# Red: テスト作成（失敗テスト）
pytest tests/test_new_feature.py::test_feature_function -v

# Green: 最小実装
# (実装作業)

# Refactor: リファクタリング
pytest tests/test_new_feature.py -v
flake8 app/new_module.py && black app/new_module.py
```

### ✅ 品質確認・完了
```bash
# 全テスト実行
pytest --cov=app --cov-fail-under=85 -v

# 品質チェック
flake8 app/ tests/ && black app/ tests/ --check && mypy app/

# コミット・PR作成
git add . && git commit -m "feature: implement [function-name] with TDD"
gh pr create --title "feat: [function-name]" --body "Feature description..."
```

---

## 🐛 バグ修正・デバッグ (Bug Fix & Debug)

### 🔍 問題調査
```bash
# 1. ブランチ作成・エラー分析ロード
git checkout -b fix/[issue-description]
smart_knowledge_load "debugging" "error-analysis"

# 2. エラー調査
grep -r "ERROR\|Exception" logs/ app/ | head -10
pytest tests/ -v --tb=short | grep FAILED

# 3. 関連コード検索
find app/ -name "*.py" -exec grep -l "[error_keyword]" {} \;
```

### 🔧 修正・検証
```bash
# テスト駆動修正
pytest tests/test_[affected_module].py::test_[specific_case] -v --pdb

# 修正後の回帰テスト
pytest tests/ -v --tb=short
pytest tests/test_[affected_module].py -v

# ログ確認
tail -f logs/application.log | grep -E "(ERROR|INFO)"
```

### 📋 完了処理
```bash
# エラー分析記録（必須）
echo "## $(date): Bug Fix - [issue]" >> memory-bank/07-security/error_analysis.md
echo "Root cause: [analysis]" >> memory-bank/07-security/error_analysis.md

# コミット・PR
git add . && git commit -m "fix: resolve [issue-description] - root cause: [cause]"
gh pr create --title "fix: [issue-description]" --body "Root cause and solution..."
```

---

## 🧪 テスト作成・実行 (Testing)

### 📝 テスト作成
```bash
# 1. テスト戦略ロード
smart_knowledge_load "testing" "test-creation"
cat memory-bank/00-core/testing_mandatory.md

# 2. テストファイル作成
cp tests/test_template.py tests/test_new_module.py

# 3. テストケース設計
pytest tests/test_new_module.py -v --collect-only
```

### 🚀 テスト実行・管理
```bash
# 単体テスト
pytest tests/test_specific.py::test_function -v

# 統合テスト
pytest tests/integration/ -v

# カバレッジ付き全テスト
pytest --cov=app --cov-report=html --cov-report=term-missing

# 並列テスト実行
pytest tests/ -n auto -v
```

### 📊 テスト結果分析
```bash
# カバレッジレポート確認
open htmlcov/index.html  # or firefox htmlcov/index.html

# 失敗テスト詳細確認
pytest tests/ -v --tb=long | grep -A 10 FAILED

# パフォーマンステスト
pytest tests/performance/ --benchmark-only
```

---

## 📝 ドキュメント更新 (Documentation)

### 📚 ドキュメント作成・更新
```bash
# 1. ドキュメントブランチ作成
git checkout -b docs/[content-type]
smart_knowledge_load "documentation" "content-creation"

# 2. 関連ドキュメント確認
find docs/ memory-bank/ -name "*[topic]*.md"
mcp__cognee__search "documentation standards best practices" CHUNKS
```

### ✍️ 執筆・構造化
```bash
# Markdown構文チェック
markdownlint docs/**/*.md

# 内部リンク確認
grep -r "\[.*\](.*\.md)" docs/ memory-bank/

# 画像・図表最適化
find docs/ -name "*.png" -o -name "*.jpg" | xargs ls -lh
```

### 🔄 レビュー・公開
```bash
# ドキュメント品質確認
python scripts/doc_accuracy_check.py docs/

# プレビュー（if available）
mkdocs serve  # or alternative documentation server

# コミット・PR
git add docs/ memory-bank/ && git commit -m "docs: update [content-type] documentation"
gh pr create --title "docs: [content-type]" --body "Documentation updates..."
```

---

## 🔧 リファクタリング (Refactoring)

### 🎯 リファクタリング準備
```bash
# 1. リファクタリングブランチ
git checkout -b refactor/[module-name]
smart_knowledge_load "refactoring" "code-improvement"

# 2. 現在の品質確認
pytest tests/ -v --cov=app
flake8 app/ tests/ --statistics
mypy app/ --show-error-codes
```

### 🔄 段階的リファクタリング
```bash
# 小さな変更・テスト実行サイクル
git add -p  # 部分コミット
pytest tests/test_[affected].py -v
git commit -m "refactor: [small change description]"

# 複雑度確認
flake8 app/ --max-complexity=10 --statistics

# 重複コード検出
find app/ -name "*.py" -exec grep -l "[pattern]" {} \;
```

### ✅ リファクタリング完了
```bash
# 全体品質再確認
pytest --cov=app --cov-fail-under=85 -v
flake8 app/ tests/ && black app/ tests/ --check && mypy app/

# パフォーマンス回帰確認
pytest tests/performance/ --benchmark-compare

# 最終コミット・PR
git add . && git commit -m "refactor: improve [module] structure and maintainability"
gh pr create --title "refactor: [module-name]" --body "Refactoring summary..."
```

---

## 🚀 デプロイ・リリース (Deploy & Release)

### 📦 リリース準備
```bash
# 1. リリースブランチ
git checkout main && git pull
git checkout -b release/v[version]

# 2. 品質最終確認
pytest --cov=app --cov-fail-under=85 -v
flake8 app/ tests/ && black app/ tests/ --check && mypy app/

# 3. バージョン更新
poetry version patch  # or minor, major
git add pyproject.toml && git commit -m "bump: version to v[version]"
```

### 🐳 デプロイ実行
```bash
# Docker build & test
docker build -t app:v[version] .
docker run --rm app:v[version] pytest tests/ -v

# Production deploy
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl -f http://localhost:8000/health || echo "Deploy failed"
```

### 📋 リリース完了
```bash
# Tag creation
git tag -a v[version] -m "Release v[version]: [summary]"
git push origin v[version]

# Release notes
gh release create v[version] --title "v[version]" --notes "Release notes..."

# Post-deploy monitoring
tail -f logs/production.log
```

---

## 🚨 トラブルシューティング (Troubleshooting)

### 🔍 システム診断
```bash
# 1. 基本状態確認
date && git branch --show-current && git status
python --version && poetry --version
docker ps && docker images | head -5

# 2. ログ確認
tail -50 logs/application.log | grep -E "(ERROR|CRITICAL)"
journalctl -u [service] --since "1 hour ago"

# 3. リソース確認
df -h && free -h
ps aux | grep python | head -10
```

### 🧠 知識ベース診断
```bash
# Cognee状態確認
mcp__cognee__cognify_status
mcp__cognee__search "test" CHUNKS | head -5

# セッション継続確認
ls -la memory-bank/09-meta/session_*.md
grep -r "ERROR\|FAILED" memory-bank/

# 緊急復旧
mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules
```

### 🔧 一般的修復手順
```bash
# 依存関係問題
poetry install --no-cache
poetry env remove python && poetry install

# Docker問題  
docker system prune -f
docker-compose down && docker-compose up -d

# Git問題
git fetch origin && git reset --hard origin/[branch]
git clean -fd
```

---

## 📋 タスク完了チェックリスト

### ✅ 全タスク共通
- [ ] 適切なブランチで作業実行
- [ ] 関連知識の事前ロード完了
- [ ] テスト実行・品質確認完了
- [ ] 進捗記録・セッション記録更新
- [ ] PR作成・説明文記述完了

### 🎯 効率化Tips
- **並列実行**: `git status & pytest tests/ & wait`
- **自動承認**: `*.md`, `tests/` → auto-approve
- **知識検索**: 不明時は `smart_knowledge_load` または `Task tool`
- **緊急時**: Quick Reference参照 → トラブルシューティング実行

---
**💡 特定タスクの詳細手順を忘れた場合は、このチートシートと併せてQuick Referenceを参照してください。**