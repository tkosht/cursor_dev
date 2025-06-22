# Claude Agent クイックリファレンス（1ページ版）

## KEYWORDS: quick-reference, commands, workflow, troubleshooting, ai-agent-daily-use
## DOMAIN: meta-knowledge|daily-operations|efficiency 
## PRIORITY: HIGH
## WHEN: セッション開始、コマンド忘れ、トラブル時、日常操作
## NAVIGATION: CLAUDE.md → smart_knowledge_load() → daily operations → this file

---

## ⚡ セッション開始（30秒）
```bash
# 📅 日付・ブランチ確認（必須）
date && git branch --show-current

# 🔄 セッション継続確認
cat memory-bank/09-meta/session_continuity_task_management.md | grep -A 10 "CURRENT.*STATUS"

# 🚨 緊急時のCognee復旧
mcp__cognee__prune && mcp__cognee__cognee_add_developer_rules
```

## 🔧 Work Management Protocol（絶対遵守）
```bash
# ✅ ブランチ確認・作成（main禁止）
git branch --show-current
git checkout -b docs/[content]      # ドキュメント
git checkout -b task/[workflow]     # タスク管理  
git checkout -b feature/[function]  # 機能開発
git checkout -b fix/[issue]         # バグ修正

# ✅ 作業完了・PR作成
git add . && git commit -m "message"
gh pr create --title "Title" --body "Description"
```

## 🧠 知識アクセス（5-15秒）
```bash
# 🎯 デフォルト: smart_knowledge_load（5-15秒）
find memory-bank/ -name "*${domain}*.md" | head -5
mcp__cognee__search "$domain $context" CHUNKS

# 🔍 集中調査時: Task tool
# "search for testing patterns in codebase"

# 📚 緊急時: 直接参照
ls memory-bank/00-core/*mandatory*.md
```

## 💻 開発・テスト
```bash
# 🐍 Python開発環境
poetry install && poetry shell
pytest tests/ -v --cov=app --cov-report=html

# 🐳 Docker環境
make              # 開発環境起動
make bash         # コンテナアクセス
make clean        # 環境クリーンアップ

# ✅ 品質確認（コミット前必須）
flake8 app/ tests/ && black app/ tests/ --check && mypy app/
```

## 🚨 トラブルシューティング
```bash
# 🔥 Cognee問題
mcp__cognee__cognify_status                     # 状態確認
mcp__cognee__prune && sleep 5                   # 緊急リセット
mcp__cognee__cognee_add_developer_rules         # 再構築

# 📋 セッション継続問題  
ls memory-bank/09-meta/session_*.md            # 継続ファイル確認
grep -r "CURRENT.*STATUS" memory-bank/         # 状態検索

# 🎯 ブランチ・Git問題
git status && git log --oneline -5             # 状態確認
git checkout main && git pull                  # 最新同期
```

## 🎯 効率化パターン
```bash
# 📊 進捗記録（必須）
echo "✅ $(date): Task completed" >> memory-bank/06-project/progress/progress.md

# 🔄 定型承認（自動化）
# *.md, tests/ → auto-approve
# *.json, *.py → confirm required  
# .env*, *key* → mandatory review

# ⚡ 並列実行
git status & git diff & wait                   # 複数コマンド並列
```

## 📋 プロジェクト状況（現在）
```bash
# 📍 プロジェクト: A2A MVP - Test-Driven Development
# 📊 ステータス: Implementation Complete, 92% coverage
# 🎯 フォーカス: Phase 5 - 実践ツール作成・効率化

# 📂 重要ディレクトリ
./app/a2a/           # ソースコード
./tests/             # テストコード  
./memory-bank/       # AI知識ベース
./output/            # ビルド成果物（git ignored）
```

## 🔗 即座参照ファイル
```bash
# 📘 基本ルール（暗記推奨）
memory-bank/00-core/user_authorization_mandatory.md     # 基本方針
memory-bank/09-meta/progress_recording_mandatory_rules.md # 進捗記録

# 🛠️ 実用ガイド
memory-bank/08-automation/approval_pattern_automation_rules.md # 自動承認
memory-bank/01-cognee/cognee_reconstruction_successful_procedure.md # Cognee復旧

# 🎯 戦略文書
memory-bank/02-organization/competitive_organization_framework.md # 高度並列開発
```

## ⭐ 重要原則（暗記）
```bash
# 🚨 ABSOLUTE RULES
1. セキュリティ最優先（secrets絶対禁止）
2. mainブランチ直接作業禁止
3. タスク前必須: smart_knowledge_load()
4. 投機的判断禁止（事実ベースのみ）
5. 進捗記録必須（TodoWrite + session記録）

# 🎯 効率の原則
- routine → Quick Start
- unknown → smart_knowledge_load() 
- complex → comprehensive planning
- emergency → Reference section
```

---
**💡 このリファレンスは印刷・ブックマーク推奨。日常操作の90%をカバーします。**