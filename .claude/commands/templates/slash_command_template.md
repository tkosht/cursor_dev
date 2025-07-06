## 🚨 MANDATORY PRE-EXECUTION CHECK

```bash
# コマンド実行前必須検証
verify_tmux_competition_mode() {
    echo "🔍 tmux組織活動コンペ方式検証中..."
    
    # tmuxセッション存在確認
    if ! tmux list-sessions 2>/dev/null | grep -q "team04"; then
        echo "❌ ERROR: team04 tmuxセッションが存在しません"
        echo "🔧 REQUIRED: tmux組織活動のコンペ方式セットアップが必要"
        return 1
    fi
    
    # worktree環境確認
    if ! git worktree list | grep -q "competitive"; then
        echo "❌ ERROR: コンペ方式worktree環境が未構築"
        echo "🔧 REQUIRED: git worktree競争環境の構築が必要"
        return 1
    fi
    
    echo "✅ tmux組織活動コンペ方式環境確認完了"
    return 0
}

# 実行前必須チェック
verify_tmux_competition_mode || {
    echo "🚨 EXECUTION BLOCKED: tmux組織活動コンペ方式が未実行"
    echo "📋 ACTION REQUIRED: 以下を実行してから再実行してください"
    echo "   1. tmux組織活動環境のセットアップ"
    echo "   2. /team04コンペ方式の初期化"
    echo "   3. git worktree競争環境の構築"
    exit 1
}
```

## 🔒 EXECUTION ENFORCEMENT

**実行条件（技術的検証）：**
- [ ] `tmux list-sessions | grep team04` = 成功必須
- [ ] `git worktree list | grep competitive` = 存在必須  
- [ ] `ls -la | grep "competitive_*"` = ディレクトリ存在必須

**違反時の自動処理：**
```bash
# 制約違反時の自動セットアップ実行
if [[ $TMUX_COMPETITION_MODE != "ACTIVE" ]]; then
    echo "🚨 CONSTRAINT VIOLATION DETECTED"
    echo "🔧 AUTO-SETUP: tmux組織活動コンペ方式を自動構築中..."
    source memory-bank/02-organization/tmux_organization_success_patterns.md
    setup_team04_competition_mode
fi
```

## ⚡ EXECUTION PRIORITY OVERRIDE

**🚨 ABSOLUTE PRIORITY（絶対優先）：**
1. **tmux組織活動コンペ方式** = 実行方法の制約（変更不可）
2. **タスク内容** = 実行対象（コンペ方式内で実行）

**実行順序（強制）：**
```bash
EXECUTION_ORDER=(
    "1. tmux組織活動環境確認・構築"
    "2. /team04コンペ方式初期化"
    "3. git worktree競争環境準備"
    "4. 14役割体制での並列タスク実行"
)
```

## 📋 TASK SPECIFICATION

{TASK_DESCRIPTION}

<theme>
$ARGUMENTS
</theme>

<meta-checklist>
- [ ] /team04 組織のコンペ方式 及び /worktree 方式の内容を精緻にかつ正確に確認
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式 及び /worktree 方式で以降のタスクを実行するためにブリーフィングを実行
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式で以下を実行
{SPECIFIC_TASKS}
- [ ] レビューを誠実にクリアしたら、コミット、プッシュし、プルリクエストを発行
- [ ] 作業用の worktree を削除します
</meta-checklist>

## 🚨 MANDATORY EXECUTION MODE

**実行方式（変更不可）：**
- **tmux組織活動コンペ方式** = 必須実行環境（技術的強制）
- **技術的検証** = `verify_tmux_competition_mode()`で確認
- **自動セットアップ** = 環境不備時の自動構築

**実行ブロック条件：**
```bash
[[ $TMUX_COMPETITION_MODE != "ACTIVE" ]] && {
    echo "🚨 EXECUTION BLOCKED: tmux組織活動コンペ方式が未実行"
    setup_team04_competition_mode
    exit 1
}
```

<constraints>
- [ ] **ABSOLUTE REQUIREMENT**: Project Manager として/team04 のtmux組織のコンペ方式 及び /worktree 方式で実行（技術的強制）
    - [ ] **TECHNICAL ENFORCEMENT**: 既存tmux を活用したコンペ方式で実施（検証関数による確認）
    - [ ] **AUTO-SETUP**: 環境不備時は自動セットアップ実行後に再開
- [ ] **EFFICIENCY ENHANCEMENT**: cognee MCP ツールを活用して情報収集の効率化を図る
- [ ] **CHECKLIST COMPLIANCE**: 本制約をチェックリスト化する
{ADDITIONAL_CONSTRAINTS}
</constraints>

## 🎯 SUCCESS CRITERIA

**完了条件：**
1. ✅ tmux組織活動コンペ方式での実行確認
2. ✅ 14役割体制での並列タスク完了
3. ✅ git worktree競争環境での成果物作成
4. ✅ 品質レビューとプルリクエスト発行
5. ✅ 作業用worktreeの適切な削除
{ADDITIONAL_SUCCESS_CRITERIA}

## 📝 TEMPLATE VARIABLES

**置換変数：**
- `{TASK_DESCRIPTION}` = タスクの概要説明
- `{SPECIFIC_TASKS}` = 具体的なタスク項目（meta-checklist内）
- `{ADDITIONAL_CONSTRAINTS}` = 追加の制約条件
- `{ADDITIONAL_SUCCESS_CRITERIA}` = 追加の成功基準

## 🛠️ USAGE GUIDELINES

**テンプレート使用方法：**
1. **基本構造の維持**: 🚨 MANDATORY PRE-EXECUTION CHECK は必須
2. **制約の強化**: 技術的検証機能は削除・変更不可
3. **カスタマイズ**: `{VARIABLE}` を具体的な内容に置換
4. **品質保証**: SUCCESS CRITERIA は必ず5項目以上設定

**命名規則：**
- ファイル名: `{command_name}.md`
- 配置場所: `.claude/commands/tasks/`
- ブランチ: `feature/slash-command-{command_name}`

## 🔧 QUALITY CHECKLIST

**テンプレート品質確認：**
- [ ] 🚨 MANDATORY PRE-EXECUTION CHECK の完全性
- [ ] 🔒 EXECUTION ENFORCEMENT の技術的強制力
- [ ] ⚡ EXECUTION PRIORITY OVERRIDE の明確性
- [ ] 📋 TASK SPECIFICATION の具体性
- [ ] 🚨 MANDATORY EXECUTION MODE の強制力
- [ ] 🎯 SUCCESS CRITERIA の明確性
- [ ] 制約の技術的検証可能性
- [ ] エラーハンドリングの完全性