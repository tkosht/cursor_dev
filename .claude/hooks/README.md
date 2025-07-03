# Claude Code Hooks for tmux Organization

このディレクトリには、tmux組織活動を効率化するためのClaude Code Hooksが含まれています。

## 🎯 目的

tmux組織活動（競争的フレームワーク）において、以下の課題を自動化で解決します：

1. **タスク実行とレビューの同期**: ファイル変更後の自動レビュー依頼
2. **Worker報告の自動化**: タスク完了時の自動報告
3. **git worktreeマージ管理**: commit後の自動マージ要求

## 📂 ファイル構成

```
.claude/hooks/
├── README.md                          # このファイル
├── settings.tmux-organization.json    # 組織活動専用Hook設定
├── tmux_organization_utils.sh         # 共通ユーティリティ関数
├── auto_review_trigger.sh             # 自動レビュー依頼
├── auto_task_report.sh                # 自動タスク報告
├── pre_commit_worktree_check.sh       # commit前チェック
├── post_commit_merge_request.sh       # commit後マージ要求
├── start_organization_context.sh      # 組織活動開始
└── stop_organization_context.sh       # 組織活動終了
```

## 🚀 使用方法

### 1. 組織活動の開始

```bash
# 組織活動コンテキストを開始
source /home/devuser/workspace/.claude/hooks/start_organization_context.sh issue-123 TaskExecutionWorker

# または特定の役割で開始
source /home/devuser/workspace/.claude/hooks/start_organization_context.sh issue-456 TaskReviewManager
```

### 2. 自動化される動作

#### ファイル変更時（PostToolUse: Write|Edit|MultiEdit）
- 自動的にレビューチームに依頼メッセージを送信
- ファイルタイプに応じたレビューフォーカスを指定
- ProjectManagerにも通知

#### Claude Codeセッション終了時（Stop）
- Workerペインからの自動タスク報告
- git状態の要約
- 作業ディレクトリ情報
- 推奨次期アクション

#### git commit前（PreToolUse: Bash with git commit）
- 競争的ブランチ命名規則チェック
- worktreeディレクトリ確認
- 大きなファイルの警告
- staging area検証

#### git commit後（PostToolUse: Bash with git commit）
- 自動マージ要求送信
- 変更統計の報告
- レビューチームへの通知
- マージ手順の提供

### 3. 組織活動の終了

```bash
# 組織活動コンテキストを終了
source /home/devuser/workspace/.claude/hooks/stop_organization_context.sh
```

## 🔧 環境変数

組織活動中は以下の環境変数が設定されます：

```bash
TMUX_ORGANIZATION_CONTEXT="competitive_framework"
TMUX_ORGANIZATION_SESSION="issue-123"
TMUX_ORGANIZATION_ROLE="TaskExecutionWorker"
```

## 📋 ログと履歴

### ログファイル
- **活動ログ**: `~/.claude/tmux_organization.log`
- **タスク報告**: `~/.claude/task_reports/`
- **マージ要求**: `~/.claude/merge_requests/`

### ログ例
```
[2025-07-02 10:45:23] TaskExecutionWorker(pane-5): AUTO_REVIEW_TRIGGER: Sent review request for app.py to pane-8
[2025-07-02 10:47:15] TaskExecutionWorker(pane-5): POST_COMMIT_MERGE: Sent merge request for branch 'competitive_exec_w1_issue123_20250702_104512' to PM pane-0
```

## 🎯 対象ペイン

### 自動検出される役割
- **ProjectManager**: `00番` または `ProjectManager`
- **ReviewManager/Worker**: `03,06,09,12番` または `TaskReview*`
- **ExecutionWorker**: `05,08,11番` または `TaskExecution*`
- **KnowledgeWorker**: `07,10,13番` または `TaskKnowledge*`

## ⚠️ 注意事項

1. **組織活動文脈でのみ動作**: `TMUX_ORGANIZATION_CONTEXT`が設定されている場合のみ
2. **tmux環境必須**: tmuxセッション内でのみ有効
3. **git環境**: git関連機能はgitリポジトリ内でのみ動作
4. **ペイン番号**: tmuxペインのタイトルで役割を識別

## 🔍 トラブルシューティング

### デバッグ方法
```bash
# ログの確認
tail -f ~/.claude/tmux_organization.log

# 環境変数の確認
echo $TMUX_ORGANIZATION_CONTEXT
echo $TMUX_ORGANIZATION_SESSION

# ペイン情報の確認
tmux list-panes -F "#{pane_index}:#{pane_title}"

# スクリプトの実行権限確認
ls -la /home/devuser/workspace/.claude/hooks/*.sh
```

### よくある問題
1. **Hooksが動作しない**: 環境変数とtmux環境を確認
2. **ペインが見つからない**: ペインタイトルの設定を確認
3. **権限エラー**: スクリプトの実行権限を確認

## 📈 効果測定

期待される効果：
- **レビュー忘れ**: 0件（自動依頼により）
- **報告忘れ**: 0件（自動報告により）
- **マージ忘れ**: 減少（自動要求により）
- **協調効率**: 30%向上（明示的通信により）

## 🔄 カスタマイズ

各スクリプトは独立しており、必要に応じて：
- メッセージ形式のカスタマイズ
- 対象ファイルタイプの変更
- 通知先の追加
- ログ形式の変更

が可能です。