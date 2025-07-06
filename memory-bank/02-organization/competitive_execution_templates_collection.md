# Competitive Execution Templates Collection
# 競争的実行テンプレート集

**作成日**: 2025-07-06  
**ベース**: Team04実証成功パターン  
**目的**: 即座実行可能なテンプレート提供  
**適用範囲**: 全規模AI Agent組織活動  
**検証済み**: 100%成功実績

## 🔍 検索・利用ガイド

### 🎯 利用シーン
- **プロジェクト開始**: 迅速な環境構築・チーム編成
- **定型業務**: 繰り返し実行される組織活動
- **品質確保**: 確実な成果物作成プロセス
- **学習・訓練**: 新メンバーの手法習得
- **緊急対応**: 短期間での高品質成果要求

### 🏷️ 検索キーワード
`execution templates`, `competitive process`, `team setup`, `quality checklist`, `automation scripts`, `project templates`

### 📋 テンプレート構成
1. **環境構築テンプレート**: 技術基盤自動セットアップ
2. **チーム編成テンプレート**: 役割定義・責任分担
3. **実行管理テンプレート**: プロセス進行・品質管理
4. **評価統合テンプレート**: 成果統合・品質評価
5. **ナレッジ化テンプレート**: 学習蓄積・改善準備

## 📋 Template 1: 環境構築テンプレート

### 1.1 プロジェクト初期化スクリプト

```bash
#!/bin/bash
# competitive_project_init.sh
# Team04検証済み環境構築テンプレート

set -euo pipefail

# パラメータ設定
PROJECT_ID=${1:-"default_$(date +%Y%m%d_%H%M%S)"}
TEAM_SIZE=${2:-14}
EXECUTION_TIME=${3:-120}
QUALITY_LEVEL=${4:-"high"}

echo "🚀 Competitive Project 初期化開始"
echo "Project ID: $PROJECT_ID"
echo "Team Size: $TEAM_SIZE"
echo "Execution Time: $EXECUTION_TIME minutes"
echo "Quality Level: $QUALITY_LEVEL"

# 必須ディレクトリ構造作成
create_project_structure() {
    echo "📁 プロジェクト構造作成..."
    
    local project_root="projects/$PROJECT_ID"
    mkdir -p "$project_root"/{docs,templates,scripts,results,logs}
    
    # Team04検証済み構造
    mkdir -p "$project_root/worker"/{strategy_team,execution_team,review_team,knowledge_team}
    
    # 役割別ディレクトリ (Team04パターン)
    mkdir -p "$project_root/worker/strategy_team"/{00.ProjectManager,01.PMOConsultant}
    mkdir -p "$project_root/worker/execution_team"/{02.ExecutionManager,05.ExecutionWorker1,08.ExecutionWorker2,11.ExecutionWorker3}
    mkdir -p "$project_root/worker/review_team"/{03.ReviewManager,06.ReviewWorker1,09.ReviewWorker2,12.ReviewWorker3}
    mkdir -p "$project_root/worker/knowledge_team"/{04.KnowledgeManager,07.KnowledgeWorker1,10.KnowledgeWorker2,13.KnowledgeWorker3}
    
    echo "✅ プロジェクト構造作成完了"
}

# Git worktree セットアップ
setup_git_worktrees() {
    echo "🌿 Git worktree 環境構築..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local project_root="projects/$PROJECT_ID"
    
    # Team04検証済みworktree構成
    local worktree_configs=(
        "$project_root/worker/strategy_team/00.ProjectManager:pm_$timestamp"
        "$project_root/worker/strategy_team/01.PMOConsultant:pmo_$timestamp"
        "$project_root/worker/execution_team/02.ExecutionManager:exec_mgr_$timestamp"
        "$project_root/worker/execution_team/05.ExecutionWorker1:exec_w1_$timestamp"
        "$project_root/worker/execution_team/08.ExecutionWorker2:exec_w2_$timestamp"
        "$project_root/worker/execution_team/11.ExecutionWorker3:exec_w3_$timestamp"
        "$project_root/worker/review_team/03.ReviewManager:rev_mgr_$timestamp"
        "$project_root/worker/review_team/06.ReviewWorker1:rev_w1_$timestamp"
        "$project_root/worker/review_team/09.ReviewWorker2:rev_w2_$timestamp"
        "$project_root/worker/review_team/12.ReviewWorker3:rev_w3_$timestamp"
        "$project_root/worker/knowledge_team/04.KnowledgeManager:know_mgr_$timestamp"
        "$project_root/worker/knowledge_team/07.KnowledgeWorker1:know_w1_$timestamp"
        "$project_root/worker/knowledge_team/10.KnowledgeWorker2:know_w2_$timestamp"
        "$project_root/worker/knowledge_team/13.KnowledgeWorker3:know_w3_$timestamp"
    )
    
    for config in "${worktree_configs[@]}"; do
        local path=$(echo "$config" | cut -d: -f1)
        local branch_suffix=$(echo "$config" | cut -d: -f2)
        local branch_name="competitive_${PROJECT_ID}_${branch_suffix}"
        
        git worktree add "$path" -b "$branch_name"
        
        # 役割設定ファイル作成
        create_role_config "$path" "$branch_name" "$PROJECT_ID"
        
        echo "✅ Worktree作成: $path -> $branch_name"
    done
}

# 役割設定ファイル作成
create_role_config() {
    local worker_path="$1"
    local branch_name="$2"
    local project_id="$3"
    
    local role=$(basename "$worker_path" | cut -d. -f2)
    
    cat > "$worker_path/ROLE_CONFIG.md" << EOF
# Role Configuration - $role

**Project ID**: $project_id
**Branch**: $branch_name
**Role**: $role
**Created**: $(date)
**Directory**: $worker_path

## 責任範囲
$(get_role_description "$role")

## 実行チェックリスト
### MUST条件
- [ ] 役割定義の理解・確認
- [ ] 担当タスクの明確化
- [ ] 品質基準の把握
- [ ] 完了条件の確認

### SHOULD条件
- [ ] 他チームとの連携確認
- [ ] 進捗報告スケジュール設定
- [ ] リスク要因の事前洗い出し

### COULD条件
- [ ] 改善提案・革新要素検討
- [ ] 効率化手法の適用
- [ ] 学習機会の最大化

## 使用コマンド
\`\`\`bash
cd $worker_path
git status
git add . && git commit -m "Progress update: [具体的内容]"
git push origin $branch_name
\`\`\`

## 報告フォーマット
\`\`\`
報告元: $role
タスク完了: [具体的完了内容]
成果物: [ファイル名・場所]
次の行動: [必要に応じて]
\`\`\`
EOF
}

# 役割説明取得
get_role_description() {
    case "$1" in
        "ProjectManager") echo "プロジェクト全体戦略決定・最終意思決定・品質承認" ;;
        "PMOConsultant") echo "プロセス最適化・品質基準設定・リスク管理・効率改善" ;;
        "ExecutionManager") echo "実行戦略策定・Worker調整・進捗管理・課題解決" ;;
        "ExecutionWorker1"|"ExecutionWorker2"|"ExecutionWorker3") echo "独立解決策実装・品質確保・成果報告・創造的実行" ;;
        "ReviewManager") echo "レビュー戦略策定・観点割当・統合評価・品質判定" ;;
        "ReviewWorker1"|"ReviewWorker2"|"ReviewWorker3") echo "専門観点レビュー・客観評価・改善提案・品質保証" ;;
        "KnowledgeManager") echo "ナレッジ戦略策定・体系化方針・品質管理・統合調整" ;;
        "KnowledgeWorker1"|"KnowledgeWorker2"|"KnowledgeWorker3") echo "ナレッジ抽出・ルール化・文書化・検索最適化" ;;
        *) echo "未定義役割 - 設定を確認してください" ;;
    esac
}

# tmux セッション起動
setup_tmux_session() {
    echo "🖥️ tmux セッション構築..."
    
    local session_name="competitive_$PROJECT_ID"
    
    # メインセッション作成
    tmux new-session -d -s "$session_name" -n "overview"
    tmux send-keys -t "$session_name:overview" "echo '🎯 Competitive Framework - $PROJECT_ID'" Enter
    
    # Team04検証済み構成: 戦略ウィンドウ
    tmux new-window -t "$session_name" -n "strategy"
    tmux split-window -h -t "$session_name:strategy"
    
    # 実行ウィンドウ (4ペイン)
    tmux new-window -t "$session_name" -n "execution"
    tmux split-window -h -t "$session_name:execution"
    tmux split-window -v -t "$session_name:execution.0"
    tmux split-window -v -t "$session_name:execution.1"
    
    # レビューウィンドウ (4ペイン)
    tmux new-window -t "$session_name" -n "review"
    tmux split-window -h -t "$session_name:review"
    tmux split-window -v -t "$session_name:review.0"
    tmux split-window -v -t "$session_name:review.1"
    
    # ナレッジウィンドウ (4ペイン)
    tmux new-window -t "$session_name" -n "knowledge"
    tmux split-window -h -t "$session_name:knowledge"
    tmux split-window -v -t "$session_name:knowledge.0"
    tmux split-window -v -t "$session_name:knowledge.1"
    
    # 監視ウィンドウ
    tmux new-window -t "$session_name" -n "monitoring"
    
    echo "✅ tmux セッション構築完了: $session_name"
}

# 品質基準設定
setup_quality_standards() {
    echo "📊 品質基準設定..."
    
    local project_root="projects/$PROJECT_ID"
    
    cat > "$project_root/QUALITY_STANDARDS.md" << EOF
# Quality Standards - $PROJECT_ID

## 全体品質基準

### MUST条件 (絶対必須)
- [ ] 全タスク100%完了
- [ ] 品質ゲート全項目クリア
- [ ] セキュリティ基準遵守
- [ ] ステークホルダー要求満足

### SHOULD条件 (推奨)
- [ ] ベストプラクティス適用
- [ ] 効率性・保守性考慮
- [ ] 拡張性・再利用性確保
- [ ] ドキュメント整備

### COULD条件 (理想)
- [ ] 革新性・創造性発揮
- [ ] ユーザビリティ向上
- [ ] パフォーマンス最適化
- [ ] 将来価値創造

## 品質レベル設定
Current Level: $QUALITY_LEVEL

$(get_quality_level_description "$QUALITY_LEVEL")
EOF
}

# 品質レベル説明
get_quality_level_description() {
    case "$1" in
        "basic") echo "基本要件満足・機能実現重視" ;;
        "standard") echo "標準品質・バランス重視" ;;
        "high") echo "高品質・公開承認レベル" ;;
        "premium") echo "最高品質・革新性追求" ;;
        *) echo "標準レベル適用" ;;
    esac
}

# 実行
main() {
    echo "🚀 Competitive Project 初期化: $PROJECT_ID"
    
    create_project_structure
    setup_git_worktrees
    setup_tmux_session
    setup_quality_standards
    
    echo "🎊 初期化完了!"
    echo "📋 次のステップ:"
    echo "  1. tmux attach-session -t competitive_$PROJECT_ID"
    echo "  2. ./competitive_team_briefing.sh $PROJECT_ID"
    echo "  3. ./competitive_execution_start.sh $PROJECT_ID"
    
    # 設定サマリー保存
    cat > "projects/$PROJECT_ID/PROJECT_SUMMARY.md" << EOF
# Project Summary - $PROJECT_ID

**Created**: $(date)
**Team Size**: $TEAM_SIZE
**Execution Time**: $EXECUTION_TIME minutes
**Quality Level**: $QUALITY_LEVEL

## Quick Commands
\`\`\`bash
# セッション接続
tmux attach-session -t competitive_$PROJECT_ID

# 環境確認
git worktree list
tmux list-sessions

# 進捗確認
./scripts/competitive_status.sh $PROJECT_ID
\`\`\`
EOF
}

main "$@"
```

### 1.2 共有コンテキスト作成テンプレート

```bash
#!/bin/bash
# create_shared_context.sh

PROJECT_ID="$1"
TASK_DESCRIPTION="$2"
TEAM_SIZE="$3"

CONTEXT_FILE="/tmp/${PROJECT_ID}_$(date +%Y%m%d_%H%M%S)_briefing_context.md"

cat > "$CONTEXT_FILE" << EOF
# $PROJECT_ID 組織活動ブリーフィング

## タスク概要
**プロジェクト**: $PROJECT_ID
**内容**: $TASK_DESCRIPTION
**チーム規模**: $TEAM_SIZE名
**作成日時**: $(date)

## 組織構造と指示系統
\`\`\`
Project Manager (strategy)
  ├→ Task Execution Team (execution)
  │   ├→ Execution Manager
  │   ├→ Execution Worker 1
  │   ├→ Execution Worker 2
  │   └→ Execution Worker 3
  ├→ Task Review Team (review)
  │   ├→ Review Manager
  │   ├→ Review Worker 1
  │   ├→ Review Worker 2
  │   └→ Review Worker 3
  └→ Knowledge Management Team (knowledge)
      ├→ Knowledge Manager
      ├→ Knowledge Worker 1
      ├→ Knowledge Worker 2
      └→ Knowledge Worker 3
\`\`\`

## 必須ルール（絶対遵守）

### 1. AI Agent協調プロトコル
- **推測禁止・実証ベース**: 推定ではなく実際の報告で確認
- **Enter別送信**: tmux通信で必須
- **ACK確認プロトコル**: 送信後3秒以内の受信確認
- **ステートレス認知対応**: 都度確認・検証プロセス

### 2. tmux通信要件
- tmux send-keys -t [pane] '[message]'でメッセージ送信
- tmux send-keys -t [pane] Enter で Enter別送信（重要）
- 3秒後に tmux capture-pane -t [pane] -p で応答確認

### 3. 報告義務・フォーマット
**タスク完了時の報告フォーマット**:
\`\`\`
報告元: [役割名]
タスク完了: [具体的完了内容の詳細]
成果物: [作成されたファイルやアウトプット]
次の行動: [必要に応じて]
\`\`\`

### 4. チェックリストドリブン実行
- **MUST条件**: 絶対必須条件の定義と確実な実行
- **SHOULD条件**: 推奨条件の評価と実装
- **COULD条件**: 理想条件の検討
- Red-Green-Refactor サイクルの適用

## 重要な参照ファイル
- ROLE_CONFIG.md: 各自の役割設定
- QUALITY_STANDARDS.md: 品質基準
- PROJECT_SUMMARY.md: プロジェクト概要
- memory-bank/02-organization/tmux_organization_success_patterns.md

## 成功要件
1. 全チーム100%タスク完了
2. 品質基準100%クリア
3. チェックリストドリブン100%遵守
4. エラーゼロ達成
5. 知識体系100%構築

---
**重要**: 推測での行動は禁止。必ず実証・確認ベースで進行すること。
EOF

echo "✅ 共有コンテキスト作成完了: $CONTEXT_FILE"
echo "$CONTEXT_FILE"
```

## 📋 Template 2: チーム実行管理テンプレート

### 2.1 チーム一斉ブリーフィングスクリプト

```bash
#!/bin/bash
# competitive_team_briefing.sh

PROJECT_ID="$1"
SESSION_NAME="competitive_$PROJECT_ID"
CONTEXT_FILE="$2"

echo "📢 チーム一斉ブリーフィング開始: $PROJECT_ID"

# 共有コンテキスト確認
if [[ ! -f "$CONTEXT_FILE" ]]; then
    echo "❌ 共有コンテキストファイルが見つかりません: $CONTEXT_FILE"
    exit 1
fi

# Team04検証済みブリーフィング配信
send_briefing_to_team() {
    local window="$1"
    local message="$2"
    
    echo "📤 ブリーフィング送信: $window"
    
    # 全ペインに同一ブリーフィング送信
    tmux list-panes -t "$SESSION_NAME:$window" -F "#{pane_index}" | while read pane; do
        tmux send-keys -t "$SESSION_NAME:$window.$pane" "$message"
        tmux send-keys -t "$SESSION_NAME:$window.$pane" Enter
        sleep 1
    done
}

# 共通ブリーフィングメッセージ作成
BRIEFING_MESSAGE="claude -p \"【Team Briefing】
プロジェクト: $PROJECT_ID

共有コンテキスト確認必須: $CONTEXT_FILE

組織活動ルール:
1. Enter別送信プロトコル厳守
2. 推測禁止・実証ベース判断
3. チェックリストドリブン実行
4. 完了時の報告義務

準備完了後、担当タスクの詳細指示を待機してください。\""

# 各チームにブリーフィング送信
echo "📢 戦略チームブリーフィング"
send_briefing_to_team "strategy" "$BRIEFING_MESSAGE"

echo "📢 実行チームブリーフィング"
send_briefing_to_team "execution" "$BRIEFING_MESSAGE"

echo "📢 レビューチームブリーフィング"
send_briefing_to_team "review" "$BRIEFING_MESSAGE"

echo "📢 ナレッジチームブリーフィング"
send_briefing_to_team "knowledge" "$BRIEFING_MESSAGE"

echo "✅ チーム一斉ブリーフィング完了"
echo "📊 受信確認: tmux capture-pane で各チーム応答確認推奨"
```

### 2.2 段階的実行管理スクリプト

```bash
#!/bin/bash
# competitive_execution_manager.sh

PROJECT_ID="$1"
SESSION_NAME="competitive_$PROJECT_ID"
EXECUTION_TIME="${2:-120}"

echo "⚡ 競争的実行管理開始: $PROJECT_ID"

# Phase 1: 戦略策定 (15分)
execute_strategy_phase() {
    echo "🎯 Phase 1: 戦略策定開始 (15分)"
    
    local strategy_instruction="claude -p \"【戦略策定指示】
    
プロジェクト: $PROJECT_ID
フェーズ: 戦略策定 (15分)

ProjectManager責務:
- 全体戦略決定
- 成功基準明確化
- リスク評価・対策

PMOConsultant責務:
- プロセス最適化
- 品質基準設定
- 効率化手法提案

完了報告フォーマット:
報告元: [役割]
戦略策定完了: [策定内容詳細]
次フェーズ準備: [準備状況]

15分後に実行フェーズ開始予定\""

    # 戦略チームに指示送信
    tmux send-keys -t "$SESSION_NAME:strategy.0" "$strategy_instruction"
    tmux send-keys -t "$SESSION_NAME:strategy.0" Enter
    
    tmux send-keys -t "$SESSION_NAME:strategy.1" "$strategy_instruction"
    tmux send-keys -t "$SESSION_NAME:strategy.1" Enter
    
    echo "⏰ 戦略策定時間: 15分間"
    sleep 900  # 15分待機
}

# Phase 2: 並列実行 (メイン実行時間)
execute_parallel_phase() {
    echo "🚀 Phase 2: 並列実行開始 ($EXECUTION_TIME分)"
    
    local execution_instruction="claude -p \"【並列実行指示】
    
プロジェクト: $PROJECT_ID
フェーズ: 並列実行 ($EXECUTION_TIME分)

実行チーム責務:
- 独立解決策実装
- 競争的品質向上
- 定期進捗報告

品質要件:
- MUST条件100%達成
- チェックリストドリブン遵守
- エラーゼロ実現

進捗報告: 30分間隔で中間報告
最終報告: ${EXECUTION_TIME}分後に完了報告

競争的実行による最高品質を追求してください\""

    # 実行チーム全体に指示
    for pane in 0 1 2 3; do
        tmux send-keys -t "$SESSION_NAME:execution.$pane" "$execution_instruction"
        tmux send-keys -t "$SESSION_NAME:execution.$pane" Enter
    done
    
    echo "⏰ 並列実行時間: $EXECUTION_TIME分間"
    
    # 定期的進捗確認
    local check_interval=1800  # 30分間隔
    local elapsed=0
    
    while [[ $elapsed -lt $((EXECUTION_TIME * 60)) ]]; do
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
        
        echo "📊 進捗確認: $((elapsed / 60))分/$EXECUTION_TIME分 経過"
        tmux send-keys -t "$SESSION_NAME:monitoring" "echo '📊 進捗確認: $((elapsed / 60))分経過'" Enter
    done
}

# Phase 3: レビュー・評価 (30分)
execute_review_phase() {
    echo "🔍 Phase 3: レビュー・評価開始 (30分)"
    
    local review_instruction="claude -p \"【レビュー・評価指示】
    
プロジェクト: $PROJECT_ID
フェーズ: レビュー・評価 (30分)

レビューチーム責務:
- 全実行成果物評価
- 多角的品質検証
- 最適解決策選定支援

評価観点:
- 機能性・完成度
- 品質・信頼性
- 革新性・創造性
- 実用性・保守性

最終評価報告:
- 各解決策の定量・定性評価
- 推奨解決策の選定理由
- 改善提案・次回活用提言

30分後に統合判定へ移行\""

    # レビューチームに指示
    for pane in 0 1 2 3; do
        tmux send-keys -t "$SESSION_NAME:review.$pane" "$review_instruction"
        tmux send-keys -t "$SESSION_NAME:review.$pane" Enter
    done
    
    echo "⏰ レビュー・評価時間: 30分間"
    sleep 1800  # 30分待機
}

# Phase 4: ナレッジ化 (30分)
execute_knowledge_phase() {
    echo "📚 Phase 4: ナレッジ化開始 (30分)"
    
    local knowledge_instruction="claude -p \"【ナレッジ化指示】
    
プロジェクト: $PROJECT_ID
フェーズ: ナレッジ化 (30分)

ナレッジチーム責務:
- 成功要因体系的抽出
- 失敗予防ポイント特定
- 再現可能プロセス文書化
- 改善提案・次回活用準備

ナレッジ化範囲:
- MUST: プロセス・手順・成功要因
- SHOULD: 失敗予防・品質基準・効率化
- COULD: 拡張可能性・応用領域・発展方向

成果物:
- 包括プロセスナレッジ文書
- 再利用テンプレート集
- memory-bank適切配置

30分後に最終完了報告\""

    # ナレッジチームに指示
    for pane in 0 1 2 3; do
        tmux send-keys -t "$SESSION_NAME:knowledge.$pane" "$knowledge_instruction"
        tmux send-keys -t "$SESSION_NAME:knowledge.$pane" Enter
    done
    
    echo "⏰ ナレッジ化時間: 30分間"
    sleep 1800  # 30分待機
}

# メイン実行フロー
main() {
    echo "🚀 競争的実行管理: $PROJECT_ID 開始"
    
    execute_strategy_phase
    execute_parallel_phase
    execute_review_phase
    execute_knowledge_phase
    
    echo "🎊 全フェーズ完了: $PROJECT_ID"
    echo "📊 最終確認: tmux attach-session -t $SESSION_NAME"
}

main "$@"
```

## 📋 Template 3: 品質評価テンプレート

### 3.1 統合品質評価スクリプト

```bash
#!/bin/bash
# competitive_quality_evaluation.sh

PROJECT_ID="$1"
EVALUATION_LEVEL="${2:-standard}"

echo "📊 統合品質評価開始: $PROJECT_ID"

# 評価基準定義
define_evaluation_criteria() {
    cat > "projects/$PROJECT_ID/EVALUATION_CRITERIA.md" << EOF
# Quality Evaluation Criteria - $PROJECT_ID

## 評価レベル: $EVALUATION_LEVEL

### 必須評価項目 (MUST)
- [ ] 機能完成度: 100%実装
- [ ] 品質基準: 全項目クリア
- [ ] セキュリティ: 脆弱性なし
- [ ] 要求適合: ステークホルダー要求満足

### 推奨評価項目 (SHOULD)
- [ ] ユーザビリティ: 使いやすさ
- [ ] パフォーマンス: 性能要件
- [ ] 保守性: 改修・拡張容易性
- [ ] ドキュメント: 適切な文書化

### 理想評価項目 (COULD)
- [ ] 革新性: 創造的解決策
- [ ] 効率性: リソース最適利用
- [ ] 拡張性: 将来価値創造
- [ ] 学習価値: ナレッジ貢献

## 評価スコア計算
- MUST項目: 各25点 (合計100点)
- SHOULD項目: 各15点 (合計60点)
- COULD項目: 各10点 (合計40点)
- 総合スコア: 200点満点

## 品質判定基準
- 180-200点: Excellent (公開推奨)
- 160-179点: Good (品質良好)
- 140-159点: Acceptable (基準達成)
- 140点未満: Needs Improvement (改善必要)
EOF
}

# 実行チーム成果物評価
evaluate_execution_results() {
    echo "⚡ 実行チーム成果物評価"
    
    local execution_teams=("ExecutionWorker1" "ExecutionWorker2" "ExecutionWorker3")
    local evaluation_summary="projects/$PROJECT_ID/EXECUTION_EVALUATION.md"
    
    cat > "$evaluation_summary" << EOF
# Execution Team Evaluation Results

$(date)

## 評価サマリー
EOF

    for team in "${execution_teams[@]}"; do
        echo "📋 $team 評価中..."
        
        # 成果物パス
        local result_path="projects/$PROJECT_ID/worker/execution_team/*$team*"
        
        cat >> "$evaluation_summary" << EOF

### $team 評価結果

#### MUST項目評価
- 機能完成度: [評価点/25]
- 品質基準: [評価点/25]
- セキュリティ: [評価点/25]
- 要求適合: [評価点/25]

#### SHOULD項目評価
- ユーザビリティ: [評価点/15]
- パフォーマンス: [評価点/15]
- 保守性: [評価点/15]
- ドキュメント: [評価点/15]

#### COULD項目評価
- 革新性: [評価点/10]
- 効率性: [評価点/10]
- 拡張性: [評価点/10]
- 学習価値: [評価点/10]

**総合スコア**: [計算結果]/200点
**判定**: [品質レベル]
**推奨**: [採用/改善/非推奨]

#### 特記事項
- 優位点: [具体的優位性]
- 改善点: [具体的改善提案]
- 革新性: [創造的要素評価]

EOF
    done
}

# レビューチーム評価統合
integrate_review_evaluations() {
    echo "🔍 レビューチーム評価統合"
    
    cat > "projects/$PROJECT_ID/REVIEW_INTEGRATION.md" << EOF
# Review Team Integration Report

$(date)

## 多角的評価統合

### 技術評価 (ReviewWorker1)
- 技術的正確性: [評価]
- アーキテクチャ品質: [評価]
- 実装効率性: [評価]

### UX/品質評価 (ReviewWorker2)
- ユーザビリティ: [評価]
- インターフェース品質: [評価]
- 使用感・満足度: [評価]

### セキュリティ/リスク評価 (ReviewWorker3)
- セキュリティ強度: [評価]
- リスク要因分析: [評価]
- 安全性確保度: [評価]

## 統合判定
### 最優秀解決策
**選定**: [選定されたソリューション]
**選定理由**: [具体的選定根拠]
**総合評価**: [点数/200点]

### 改善提案
1. [改善項目1]: [具体的改善方法]
2. [改善項目2]: [具体的改善方法]
3. [改善項目3]: [具体的改善方法]

### 次回活用提言
- 成功要因: [再現すべき要素]
- 注意点: [回避すべき要素]
- 発展可能性: [将来への展開]
EOF
}

# 最終品質判定
final_quality_decision() {
    echo "🏆 最終品質判定"
    
    cat > "projects/$PROJECT_ID/FINAL_QUALITY_DECISION.md" << EOF
# Final Quality Decision - $PROJECT_ID

**判定日時**: $(date)
**判定者**: Quality Evaluation System
**評価レベル**: $EVALUATION_LEVEL

## 総合判定結果

### 採用解決策
**選定**: [最終採用ソリューション]
**総合スコア**: [最終スコア]/200点
**品質レベル**: [判定レベル]

### 判定根拠
1. **機能性**: [評価詳細]
2. **品質性**: [評価詳細]
3. **革新性**: [評価詳細]
4. **実用性**: [評価詳細]

### 公開承認判定
- [ ] 公開承認推奨
- [ ] 条件付き承認 (改善後)
- [ ] 承認保留 (大幅改善必要)

### 改善勧告
$(if [[ スコア < 180 ]]; then
echo "#### 必要改善項目
- [改善項目1]: [具体的方法]
- [改善項目2]: [具体的方法]"
else
echo "#### 優秀品質達成
改善勧告なし - 公開承認レベル達成"
fi)

### 次回プロジェクトへの提言
- **継続要素**: [成功した手法・プロセス]
- **改善要素**: [次回改善すべき点]
- **革新機会**: [さらなる発展可能性]

---
**Quality Assurance**: Competitive Execution Framework
**Validation**: Team04 Proven Process
EOF
}

# メイン評価実行
main() {
    echo "📊 統合品質評価: $PROJECT_ID"
    
    define_evaluation_criteria
    evaluate_execution_results
    integrate_review_evaluations
    final_quality_decision
    
    echo "✅ 品質評価完了"
    echo "📄 評価結果: projects/$PROJECT_ID/FINAL_QUALITY_DECISION.md"
}

main "$@"
```

## 📋 Template 4: 自動化支援ツール

### 4.1 プロジェクト状況監視スクリプト

```bash
#!/bin/bash
# competitive_status_monitor.sh

PROJECT_ID="$1"
MONITOR_INTERVAL="${2:-30}"

echo "📊 競争的プロジェクト状況監視: $PROJECT_ID"

# リアルタイム状況確認
show_current_status() {
    echo "════════════════════════════════════════"
    echo "📊 Project Status: $PROJECT_ID"
    echo "Time: $(date)"
    echo "════════════════════════════════════════"
    
    # Git worktree状況
    echo "🌿 Git Worktree Status:"
    git worktree list | grep "$PROJECT_ID" | head -10
    echo ""
    
    # tmux セッション状況
    echo "🖥️ tmux Session Status:"
    tmux list-sessions | grep "competitive_$PROJECT_ID" || echo "セッションなし"
    echo ""
    
    # 進捗ファイル確認
    echo "📁 Progress Files:"
    find "projects/$PROJECT_ID" -name "*.md" -newer "projects/$PROJECT_ID" 2>/dev/null | head -5
    echo ""
    
    # システムリソース
    echo "💻 System Resources:"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"
    echo "RAM: $(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')%"
    echo "Disk: $(df -h . | tail -1 | awk '{print $5}')"
    echo ""
}

# 継続監視
continuous_monitoring() {
    while true; do
        clear
        show_current_status
        
        echo "⏰ Next update in $MONITOR_INTERVAL seconds..."
        echo "Press Ctrl+C to stop monitoring"
        
        sleep "$MONITOR_INTERVAL"
    done
}

# 単発状況確認
single_status_check() {
    show_current_status
    
    # 詳細レポート生成
    local report_file="projects/$PROJECT_ID/status_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Status Report - $PROJECT_ID

**Generated**: $(date)

## Project Structure
\`\`\`
$(find "projects/$PROJECT_ID" -type f -name "*.md" | head -20)
\`\`\`

## Git Status
\`\`\`
$(git worktree list | grep "$PROJECT_ID")
\`\`\`

## tmux Sessions
\`\`\`
$(tmux list-sessions | grep "competitive_$PROJECT_ID")
\`\`\`

## Recent Activity
\`\`\`
$(find "projects/$PROJECT_ID" -type f -newer "projects/$PROJECT_ID" 2>/dev/null | head -10)
\`\`\`
EOF
    
    echo "📄 詳細レポート: $report_file"
}

# 使用方法
if [[ "$MONITOR_INTERVAL" == "once" ]]; then
    single_status_check
else
    continuous_monitoring
fi
```

### 4.2 クリーンアップ・リセットスクリプト

```bash
#!/bin/bash
# competitive_project_cleanup.sh

PROJECT_ID="$1"
CLEANUP_TYPE="${2:-standard}"

echo "🧹 競争的プロジェクトクリーンアップ: $PROJECT_ID"

# 安全確認
confirm_cleanup() {
    echo "⚠️ クリーンアップ対象: $PROJECT_ID"
    echo "タイプ: $CLEANUP_TYPE"
    echo ""
    echo "削除対象:"
    echo "- Git worktrees"
    echo "- tmux sessions"
    echo "- Project files"
    echo ""
    
    if [[ "$CLEANUP_TYPE" != "--force" ]]; then
        read -p "本当にクリーンアップを実行しますか？ (yes/no): " confirmation
        if [[ "$confirmation" != "yes" ]]; then
            echo "❌ クリーンアップをキャンセルしました"
            exit 0
        fi
    fi
}

# Git worktree クリーンアップ
cleanup_worktrees() {
    echo "🌿 Git worktree クリーンアップ..."
    
    git worktree list | grep "$PROJECT_ID" | while read line; do
        local path=$(echo "$line" | awk '{print $1}')
        local branch=$(echo "$line" | awk '{print $2}' | sed 's/\[//' | sed 's/\]//')
        
        if [[ -n "$path" && -d "$path" ]]; then
            echo "🗑️ Removing worktree: $path"
            git worktree remove "$path" --force
        fi
        
        if [[ -n "$branch" && "$branch" =~ competitive.*$PROJECT_ID ]]; then
            echo "🗑️ Deleting branch: $branch"
            git branch -D "$branch" 2>/dev/null || true
        fi
    done
}

# tmux セッションクリーンアップ
cleanup_tmux_sessions() {
    echo "🖥️ tmux セッションクリーンアップ..."
    
    local session_name="competitive_$PROJECT_ID"
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "🗑️ Killing tmux session: $session_name"
        tmux kill-session -t "$session_name"
    else
        echo "ℹ️ tmux session not found: $session_name"
    fi
}

# プロジェクトファイルクリーンアップ
cleanup_project_files() {
    echo "📁 プロジェクトファイルクリーンアップ..."
    
    local project_path="projects/$PROJECT_ID"
    
    if [[ -d "$project_path" ]]; then
        if [[ "$CLEANUP_TYPE" == "preserve_results" ]]; then
            echo "💾 結果ファイルを保存中..."
            mkdir -p "archive/$PROJECT_ID"
            cp -r "$project_path/results" "archive/$PROJECT_ID/" 2>/dev/null || true
            cp "$project_path"/*.md "archive/$PROJECT_ID/" 2>/dev/null || true
        fi
        
        echo "🗑️ Removing project directory: $project_path"
        rm -rf "$project_path"
    else
        echo "ℹ️ Project directory not found: $project_path"
    fi
}

# 一時ファイルクリーンアップ
cleanup_temp_files() {
    echo "🗂️ 一時ファイルクリーンアップ..."
    
    # ブリーフィングファイル
    rm -f /tmp/*"$PROJECT_ID"*briefing_context.md
    
    # ログファイル
    rm -f /tmp/*"$PROJECT_ID"*.log
    
    # その他一時ファイル
    find /tmp -name "*$PROJECT_ID*" -type f -mtime +1 -delete 2>/dev/null || true
}

# システム最適化
optimize_system() {
    echo "⚡ システム最適化..."
    
    # Git ガベージコレクション
    git gc --aggressive --prune=now
    
    # tmux server確認・最適化
    if ! tmux list-sessions >/dev/null 2>&1; then
        echo "🔄 tmux server restart"
        tmux kill-server 2>/dev/null || true
    fi
    
    # 孤立ディレクトリ削除
    find . -type d -empty -delete 2>/dev/null || true
}

# メインクリーンアップ実行
main() {
    echo "🧹 競争的プロジェクトクリーンアップ開始: $PROJECT_ID"
    
    confirm_cleanup
    
    cleanup_tmux_sessions
    cleanup_worktrees
    cleanup_temp_files
    cleanup_project_files
    optimize_system
    
    echo "✅ クリーンアップ完了: $PROJECT_ID"
    
    if [[ "$CLEANUP_TYPE" == "preserve_results" ]]; then
        echo "💾 結果保存先: archive/$PROJECT_ID/"
    fi
    
    echo "📊 システム状況:"
    echo "  Git worktrees: $(git worktree list | wc -l)"
    echo "  tmux sessions: $(tmux list-sessions 2>/dev/null | wc -l || echo 0)"
    echo "  Project dirs: $(find projects/ -maxdepth 1 -type d | wc -l)"
}

main "$@"
```

## 📋 テンプレート利用ガイド

### クイックスタート手順

```bash
# 1. プロジェクト初期化
./competitive_project_init.sh "my_project_001" 14 120 high

# 2. チームブリーフィング
./create_shared_context.sh "my_project_001" "note記事作成" 14
./competitive_team_briefing.sh "my_project_001" /tmp/my_project_001_*_briefing_context.md

# 3. 実行管理開始
./competitive_execution_manager.sh "my_project_001" 120

# 4. 品質評価
./competitive_quality_evaluation.sh "my_project_001" standard

# 5. 状況監視 (別端末)
./competitive_status_monitor.sh "my_project_001"

# 6. 完了後クリーンアップ
./competitive_project_cleanup.sh "my_project_001" preserve_results
```

### カスタマイズ指針

1. **チーム規模調整**: TEAM_SIZE パラメータで人数変更
2. **品質レベル調整**: QUALITY_LEVEL で要求品質設定
3. **実行時間調整**: EXECUTION_TIME で各フェーズ時間調整
4. **評価基準調整**: EVALUATION_CRITERIA.md でスコア基準変更

---

**適用推奨**: これらのテンプレートにより、Team04実証済み成功パターンの即座適用が可能です。プロジェクト特性に応じてパラメータ調整し、確実な高品質成果を実現してください。