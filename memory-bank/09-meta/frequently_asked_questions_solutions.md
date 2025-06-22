# よくある質問と解決策（FAQ）

## KEYWORDS: faq, troubleshooting, common-issues, solutions, ai-agent-support
## DOMAIN: meta-knowledge|support|troubleshooting
## PRIORITY: MEDIUM
## WHEN: 問題発生時、不明点がある時、新しい課題に直面した時
## NAVIGATION: CLAUDE.md → smart_knowledge_load() → troubleshooting → this file

---

## 🔧 セットアップ・環境関連

### Q1: セッション開始時に何から始めればいいですか？
**A**: Quick Startの30秒セットアップを実行：
```bash
# 1. 日付・ブランチ確認
date && git branch --show-current

# 2. セッション継続確認  
cat memory-bank/09-meta/session_continuity_task_management.md | grep -A 10 "CURRENT.*STATUS"

# 3. 必要に応じてCognee復旧
mcp__cognee__cognify_status || (mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules)
```

### Q2: Cogneeが動作しない・エラーが出ます
**A**: 段階的復旧を実行：
```bash
# Step 1: 状態確認
mcp__cognee__cognify_status

# Step 2: 軽度な問題の場合
mcp__cognee__cognee_add_developer_rules

# Step 3: 深刻な問題の場合  
mcp__cognee__prune && sleep 5 && mcp__cognee__cognee_add_developer_rules

# Step 4: 完全復旧手順（45分）
# 詳細: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md
```

### Q3: どのブランチで作業すべきですか？
**A**: 作業タイプ別にブランチを作成（main禁止）：
```bash
git checkout -b docs/[content-type]      # ドキュメント作業
git checkout -b task/[workflow-type]     # タスク管理・プロセス改善
git checkout -b feature/[function-name]  # 新機能開発
git checkout -b fix/[issue-description]  # バグ修正
```

---

## 📚 知識アクセス関連

### Q4: 必要な知識をどう見つければいいですか？
**A**: 3段階アプローチ：
```bash
# Level 1: デフォルト（5-15秒）
smart_knowledge_load "domain" "context"

# Level 2: 調査が必要（Task tool使用）
# "search for testing patterns in codebase"

# Level 3: 緊急時・直接参照
ls memory-bank/00-core/*mandatory*.md
find memory-bank/ -name "*[keyword]*.md"
```

### Q5: smart_knowledge_load vs comprehensive_knowledge_load の使い分けは？
**A**: 基本的にsmart_knowledge_load、例外的にcomprehensive：
- **smart_knowledge_load**: 全タスクのデフォルト（5-15秒、90%ニーズ対応）
- **comprehensive_knowledge_load**: ユーザーが明示的に詳細分析を要求した時のみ（30-60秒）

### Q6: どのファイルが最も重要ですか？
**A**: 必須ファイル優先順位：
1. `CLAUDE.md` - 基本プロトコル
2. `memory-bank/00-core/*mandatory*.md` - 必須ルール
3. `memory-bank/09-meta/session_continuity_task_management.md` - セッション継続
4. `memory-bank/09-meta/claude_agent_quick_reference.md` - 日常操作

---

## 🔄 ワークフロー関連

### Q7: タスクを途中で中断した場合、どう再開しますか？
**A**: セッション継続プロトコル：
```bash
# 1. 前回状況確認
cat memory-bank/09-meta/session_continuity_task_management.md

# 2. TodoRead確認  
# TodoReadを実行して中断タスクを確認

# 3. 知識再ロード
smart_knowledge_load "[domain]" "[context]"

# 4. 作業再開
git branch --show-current  # ブランチ確認
```

### Q8: Pull Requestの作成タイミングは？
**A**: 各Phase・機能完了時に必須：
```bash
# 作業完了確認
pytest --cov=app --cov-fail-under=85 -v
flake8 app/ tests/ && black app/ tests/ --check

# PR作成
git add . && git commit -m "descriptive message"
gh pr create --title "Title" --body "Description"
```

### Q9: 進捗記録はどの程度詳細に書くべきですか？
**A**: 目的別に調整：
- **TodoWrite**: リアルタイム進捗（簡潔）
- **session_continuity**: セッション間継続（中程度）
- **memory-bank/06-project/progress/**: プロジェクト記録（詳細）

---

## 🐛 トラブルシューティング

### Q10: テストが失敗します
**A**: 段階的デバッグ：
```bash
# 1. 特定テスト実行
pytest tests/test_module.py::test_function -v --tb=short

# 2. デバッグモード
pytest tests/test_module.py::test_function -v --pdb

# 3. カバレッジ確認
pytest tests/test_module.py --cov=app.module --cov-report=term-missing

# 4. 依存関係確認
poetry check && poetry install
```

### Q11: Gitで問題が発生しました
**A**: 状況別対処：
```bash
# 基本状況確認
git status && git log --oneline -5

# コンフリクト解決
git pull origin main && git mergetool

# 変更取り消し
git checkout -- [file]  # ファイル単位
git reset --hard HEAD~1  # コミット取り消し（注意）

# 緊急避難
git stash && git checkout main && git pull
```

### Q12: Docker環境で問題があります
**A**: 段階的修復：
```bash
# 1. 状況確認
docker ps && docker images | head -5

# 2. 軽度な問題
docker-compose restart

# 3. 中程度な問題  
docker-compose down && docker-compose up -d

# 4. 深刻な問題
docker system prune -f && docker-compose up --build
```

---

## ⚡ 効率化・最適化

### Q13: 作業を高速化したいです
**A**: 効率化テクニック：
```bash
# 並列実行
git status & pytest tests/ & mcp__cognee__cognify_status & wait

# 自動承認活用
# *.md, tests/ → 自動承認
# *.json, scripts/ → 確認要求

# ショートカット活用
alias gs="git status"
alias gco="git checkout"
alias pr="gh pr create"
```

### Q14: よく使うコマンドを忘れます
**A**: リファレンス活用：
- `memory-bank/09-meta/claude_agent_quick_reference.md` - 1ページ版
- `memory-bank/09-meta/task_specific_command_cheatsheet.md` - タスク別
- CLAUDE.md Essential Commands セクション

### Q15: 複雑なタスクで迷います
**A**: 段階的アプローチ：
```bash
# 1. 問題分解
# Phase 1: Must Have（最小限）
# Phase 2: Should Have（改善）  
# Phase 3: Could Have（最適化）

# 2. 知識収集
smart_knowledge_load "[domain]" "[context]"
mcp__cognee__search "[topic] best practices" RAG_COMPLETION

# 3. Task tool活用
# "analyze this complex problem and suggest approach"
```

---

## 🚨 エラー・緊急時

### Q16: 「Database not created」エラーが出ます
**A**: Cognee初期化エラー対応：
```bash
# 即座実行
mcp__cognee__prune && sleep 10 && mcp__cognee__cognee_add_developer_rules

# 状況確認
mcp__cognee__cognify_status

# 完全復旧（必要な場合）
# 詳細手順: memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md
```

### Q17: 「Permission denied」エラーが出ます
**A**: 権限問題対応：
```bash
# ファイル権限確認
ls -la [file_path]

# 一般的な修復
chmod +x scripts/*.sh
sudo chown -R $USER:$USER [directory]

# Docker関連の場合
sudo usermod -aG docker $USER && newgrp docker
```

### Q18: メモリ不足・パフォーマンス問題があります
**A**: リソース最適化：
```bash
# リソース確認
free -h && df -h
ps aux --sort=-%mem | head -10

# Cognee最適化
# 詳細: memory-bank/01-cognee/search_speed_optimization_and_indexing_strategy.md

# 一般的クリーンアップ
docker system prune -f
poetry cache clear --all pypi
```

---

## 📋 ベストプラクティス

### Q19: 品質を保つためのコツは？
**A**: 品質維持戦略：
- **TDD**: テスト先行開発（Red-Green-Refactor）
- **小さなコミット**: 機能単位の細かいコミット
- **自動化**: 品質チェックの自動化活用
- **レビュー**: セルフレビューの徹底

### Q20: プロジェクト全体の見通しを良くするには？
**A**: 可視化・管理技術：
```bash
# 進捗確認
cat memory-bank/06-project/progress/progress.md

# ブランチ状況
git branch -a && git log --oneline --graph -10

# テストカバレッジ  
pytest --cov=app --cov-report=term-missing

# ToDo状況
# TodoRead実行
```

---

## 🔗 関連リソース

### 📚 主要参照ファイル
- **CLAUDE.md**: 基本プロトコル・Quick Start
- **memory-bank/09-meta/claude_agent_quick_reference.md**: 日常操作
- **memory-bank/09-meta/task_specific_command_cheatsheet.md**: タスク別手順
- **memory-bank/01-cognee/**: Cognee関連全般

### 🆘 緊急時対応
1. **Cognee問題**: `memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md`
2. **Git問題**: `memory-bank/08-automation/git_troubleshooting_patterns.md`  
3. **品質問題**: `memory-bank/04-quality/debugging_best_practices.md`
4. **セキュリティ**: `memory-bank/07-security/security_incident_knowledge.md`

---

**💡 この FAQ で解決しない場合は、Task tool を使用して「troubleshoot [specific problem]」で詳細調査を実行してください。**