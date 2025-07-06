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

# 🔧 AUTOMATIC ENFORCEMENT IMPLEMENTATION
$(
    echo "🔍 note_article実行開始 - 強制検証・自動セットアップ実行中..."
    
    # 即座に検証実行
    if ! tmux list-sessions 2>/dev/null | grep -q "team04"; then
        echo "🚨 BLOCKING: team04セッション未発見 - 自動作成開始"
        tmux new-session -d -s team04 -x 120 -y 40
        tmux split-window -h -t team04:0
        tmux split-window -v -t team04:0.0
        tmux split-window -v -t team04:0.1
        echo "✅ team04セッション自動作成完了"
    fi
    
    if ! git worktree list | grep -q "competitive"; then
        echo "🚨 BLOCKING: competitive worktree未発見 - 自動作成開始"
        git worktree add competitive-work HEAD
        echo "✅ competitive worktree自動作成完了"
    fi
    
    # 4役割体制の自動セットアップ
    echo "🔧 4役割体制セットアップ中..."
    
    # 各ペインに役割を割り当て（Enter別送信遵守）
    tmux send-keys -t team04:0.0 "echo 'Project Manager - tmux組織活動コンペ方式実行中'"
    tmux send-keys -t team04:0.0 Enter
    
    tmux send-keys -t team04:0.1 "echo 'Task Worker 1 - 記事A: tmux基礎概念'"
    tmux send-keys -t team04:0.1 Enter
    
    tmux send-keys -t team04:0.2 "echo 'Task Worker 2 - 記事B: 実践事例'"
    tmux send-keys -t team04:0.2 Enter
    
    tmux send-keys -t team04:0.3 "echo 'Task Worker 3 - 記事C: 技術詳細'"
    tmux send-keys -t team04:0.3 Enter
    
    # 検証待機（Enter別送信確認）
    sleep 3
    
    export TMUX_COMPETITION_MODE="ACTIVE"
    echo "✅ 4役割体制構築完了 - 並列記事作成開始"
    echo "✅ 強制検証・自動セットアップ完了 - 実行継続"
)

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

## 🚨 AIエージェント向け絶対実行制約

### ❌ 絶対禁止事項
```bash
# 以下のツールは note_article では使用禁止
FORBIDDEN_TOOLS=("Write" "Edit" "MultiEdit" "NotebookEdit")

# 禁止理由: tmux ペインでの作業が技術的強制事項
# 違反時: 即座に停止・修正が必要
```

### ✅ 必須実行パターン
```bash
# 1. 環境確認・自動セットアップ
tmux list-sessions | grep team04 || auto_setup_team04
git worktree list | grep competitive || auto_setup_competitive

# 2. Project Manager としてのブリーフィング実行
tmux send-keys -t team04:0.0 "cd /home/devuser/workspace/competitive-work"
tmux send-keys -t team04:0.0 Enter
tmux send-keys -t team04:0.0 "echo 'PM: note_article タスク開始 - 4役割体制実行'"
tmux send-keys -t team04:0.0 Enter

# 3. 各ワーカーへのタスク配布（Enter別送信遵守）
tmux send-keys -t team04:0.1 "cd /home/devuser/workspace/competitive-work"
tmux send-keys -t team04:0.1 Enter
tmux send-keys -t team04:0.1 "vim section_A_basics.md"
tmux send-keys -t team04:0.1 Enter

tmux send-keys -t team04:0.2 "cd /home/devuser/workspace/competitive-work"
tmux send-keys -t team04:0.2 Enter
tmux send-keys -t team04:0.2 "vim section_B_examples.md"
tmux send-keys -t team04:0.2 Enter

tmux send-keys -t team04:0.3 "cd /home/devuser/workspace/competitive-work"
tmux send-keys -t team04:0.3 Enter
tmux send-keys -t team04:0.3 "vim section_C_technical.md"
tmux send-keys -t team04:0.3 Enter

# 4. 各ペインでの実際の記事作成作業
# Project Manager: 全体調整とレビュー
# Task Worker 1: 基礎概念部分
# Task Worker 2: 実践事例部分  
# Task Worker 3: 技術詳細部分

# 5. 統合と完成
tmux send-keys -t team04:0.0 "cat section_A_basics.md section_B_examples.md section_C_technical.md > final_note_article.md"
tmux send-keys -t team04:0.0 Enter
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
    auto_setup_team04_competition_mode
fi

# 禁止ツール使用検出
if [[ $TOOL_NAME == "Write" || $TOOL_NAME == "Edit" || $TOOL_NAME == "MultiEdit" ]]; then
    echo "🚨 VIOLATION DETECTED: $TOOL_NAME は note_article では使用禁止"
    echo "📋 CORRECTION: tmux ペインでの作業に切り替えてください"
    exit 1
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
    "4. 4役割体制での並列タスク実行"
    "5. tmux ペイン内での実際の記事作成"
)
```

## 📋 TASK SPECIFICATION

<theme/> に関する 本リポジトリのナレッジ・ルール・文書を洗い出し、内容を整理して <constraints/> を厳守し note 記事として作成します。

<theme>
$ARGUMENTS
</theme>

<meta-checklist>
- [ ] /team04 組織のコンペ方式 及び /worktree 方式の内容を精緻にかつ正確に確認
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式 及び /worktree 方式で以降のタスクを実行するためにブリーフィングを実行
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式で以下を実行
    - [ ] note 記事の書き方について、ナレッジ・ルール・文書を洗い出し内容を精緻かつ正確に整理
        - [ ] ターゲットが特に指定されていない場合は、ビジネスユーザを対象として、該当テーマについては初学者～中級者の間の層を対象
        - [ ] どうしても高度な内容を説明する必要がある場合は、ターゲットユーザに配慮した記述とすること
    - [ ] <theme/> に関連するナレッジ・ルール・文書を洗い出し内容を精緻かつ正確に整理
    - [ ] <theme/> に関連して、Web 上を精緻に検索し一般的な情報を精緻かつ正確に整理
    - [ ] チェックリストドリブンで実行するためのチェックリストを精緻に設計し作成
        - [ ] レビュー観点も洗い出し、レビュー観点についてもチェックリストに含める
        - [ ] 特に、ターゲットユーザ視点で読みたくなるか、わくわくして続きをどんどん読みたくなる構成になっているか評価してください
        - [ ] また、本コマンド説明の <constraints/> をチェックリスト化してください
    - [ ] チェックリストドリブンで実行するためのチェックリストを精緻に設計し作成
    - [ ] /do_task 方式に従いタスクを実行
    - [ ] レビュー観点に従いレビューを行い改善サイクルを回す
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
    - [ ] **FORBIDDEN TOOLS**: Write/Edit/MultiEdit ツールの使用禁止
    - [ ] **MANDATORY TMUX WORK**: 全作業を tmux ペイン内で実行
- [ ] **EFFICIENCY ENHANCEMENT**: cognee MCP ツールを活用して情報収集の効率化を図る
- [ ] **CHECKLIST COMPLIANCE**: 本制約をチェックリスト化する
</constraints>

## 🎯 SUCCESS CRITERIA

**完了条件：**
1. ✅ tmux組織活動コンペ方式での実行確認
2. ✅ 4役割体制での並列タスク完了
3. ✅ git worktree競争環境での成果物作成
4. ✅ 品質レビューとプルリクエスト発行
5. ✅ 作業用worktreeの適切な削除

**成功確認：**
```bash
# 作業完了の確認
tmux capture-pane -t team04:0.0 -p | tail -5
tmux capture-pane -t team04:0.1 -p | tail -5
tmux capture-pane -t team04:0.2 -p | tail -5
tmux capture-pane -t team04:0.3 -p | tail -5

# ファイル作成確認
ls -la competitive-work/section_*.md
ls -la competitive-work/final_note_article.md
```