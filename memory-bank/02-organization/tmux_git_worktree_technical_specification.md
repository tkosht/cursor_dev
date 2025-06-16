# tmux + git worktree 技術仕様書 - コンペ方式並列実行システム

**作成日**: 2025-06-17  
**対象**: 並列開発・レビュー・ナレッジ化技術基盤  
**目的**: tmux多重実行とgit worktree分離による競争環境の技術実現  
**重要度**: ★★★★★ TECHNICAL FOUNDATION

## 🔍 検索・利用ガイド

### 🎯 **利用シーン**
- **並列開発**: 複数解決策の同時開発環境構築
- **技術基盤構築**: tmux + git worktree システムセットアップ
- **環境設定**: 開発・レビュー・ナレッジ化環境の技術設計
- **トラブルシューティング**: 並列環境の問題解決
- **パフォーマンス最適化**: システム効率の向上

### 🏷️ **検索キーワード**
`tmux parallel execution`, `git worktree setup`, `competitive development environment`, `tmux session management`, `branch isolation`, `parallel workflow`, `workspace organization`, `technical infrastructure`, `development environment`, `collaboration tools`

### 📋 **関連ファイル**
- **組織フレームワーク**: `memory-bank/02-organization/competitive_organization_framework.md`
- **tmux基盤**: `memory-bank/02-organization/tmux_claude_agent_organization.md`
- **委譲システム**: `memory-bank/02-organization/delegation_decision_framework.md`
- **品質管理**: `memory-bank/04-quality/critical_review_framework.md`

### ⚡ **クイックアクセス**
```bash
# 環境確認
tmux --version && git --version

# 即座実行（CLAUDE.mdから）
./scripts/tmux_worktree_setup.sh issue-123
./scripts/tmux_session_start.sh issue-123

# 状況確認
tmux list-sessions && git worktree list

# 緊急修復
./scripts/tmux_worktree_repair.sh --force-clean

# 導線ガイド
echo "📖 Entry point: CLAUDE.md → Competitive Organization (Advanced Mode)"
echo "📋 Framework: competitive_organization_framework.md"
echo "👥 Roles: competitive_roles_workflows_specification.md"
echo "🏅 Quality: competitive_quality_evaluation_framework.md"
```

## 🎯 技術アーキテクチャ概要

### システム設計思想
tmux + git worktree システムは、**完全分離された並列開発環境**を提供し、競争的開発における**依存関係の排除**と**独立性の確保**を実現します。各Workerが独立したブランチ・ワークスペース・セッションを持つことで、真の並列実行と客観的比較評価を可能にします。

### 核心技術要素
- **tmux Multi-Session**: 独立した作業環境の並列管理
- **git worktree**: 同一リポジトリの複数作業ツリー分離
- **Branch Isolation**: ブランチ単位の完全独立性
- **Resource Management**: システムリソースの効率配分

## 1. git worktree 設計仕様

### 1.1 ディレクトリ構造・ブランチ戦略

#### 物理ディレクトリ構造
```bash
/home/devuser/workspace/
├── .git/                                    # メインリポジトリ
├── worker/                                  # worktree管理ディレクトリ
│   ├── strategy_team/
│   │   ├── 00.ProjectManager/              # worktree: competitive_pm_YYYYMMDD_HHMMSS
│   │   └── 01.PMOConsultant/               # worktree: competitive_pmo_YYYYMMDD_HHMMSS
│   ├── execution_team/
│   │   ├── 02.TaskExecutionManager/        # worktree: competitive_exec_mgr_YYYYMMDD_HHMMSS
│   │   ├── 05.TaskExecutionWorker/         # worktree: competitive_exec_w1_YYYYMMDD_HHMMSS
│   │   ├── 08.TaskExecutionWorker/         # worktree: competitive_exec_w2_YYYYMMDD_HHMMSS
│   │   └── 11.TaskExecutionWorker/         # worktree: competitive_exec_w3_YYYYMMDD_HHMMSS
│   ├── review_team/
│   │   ├── 03.TaskReviewManager/           # worktree: competitive_rev_mgr_YYYYMMDD_HHMMSS
│   │   ├── 06.TaskReviewWorker/            # worktree: competitive_rev_w1_YYYYMMDD_HHMMSS
│   │   ├── 09.TaskReviewWorker/            # worktree: competitive_rev_w2_YYYYMMDD_HHMMSS
│   │   └── 12.TaskReviewWorker/            # worktree: competitive_rev_w3_YYYYMMDD_HHMMSS
│   └── knowledge_rule_team/
│       ├── 04.TaskKnowledgeRuleManager/    # worktree: competitive_know_mgr_YYYYMMDD_HHMMSS
│       ├── 07.TaskKnowledgeRuleWorker/     # worktree: competitive_know_w1_YYYYMMDD_HHMMSS
│       ├── 10.TaskKnowledgeRuleWorker/     # worktree: competitive_know_w2_YYYYMMDD_HHMMSS
│       └── 13.TaskKnowledgeRuleWorker/     # worktree: competitive_know_w3_YYYYMMDD_HHMMSS
└── scripts/                                # 管理スクリプト
    ├── tmux_worktree_setup.sh
    ├── competitive_branch_manager.sh
    └── worktree_cleanup.sh
```

#### ブランチ命名規則
```bash
# ブランチ命名パターン
competitive_{role}_{issue_id}_{timestamp}

# 例：
competitive_exec_w1_issue123_20250617_143022
competitive_rev_w2_issue123_20250617_143045
competitive_know_mgr_issue123_20250617_143102

# ブランチ構造
main
├── competitive_pm_issue123_20250617_143022      # ProjectManager
├── competitive_pmo_issue123_20250617_143022     # PMOConsultant
├── competitive_exec_mgr_issue123_20250617_143022 # ExecutionManager
├── competitive_exec_w1_issue123_20250617_143022  # ExecutionWorker1
├── competitive_exec_w2_issue123_20250617_143022  # ExecutionWorker2
├── competitive_exec_w3_issue123_20250617_143022  # ExecutionWorker3
├── competitive_rev_mgr_issue123_20250617_143022  # ReviewManager
├── competitive_rev_w1_issue123_20250617_143022   # ReviewWorker1
├── competitive_rev_w2_issue123_20250617_143022   # ReviewWorker2
├── competitive_rev_w3_issue123_20250617_143022   # ReviewWorker3
├── competitive_know_mgr_issue123_20250617_143022 # KnowledgeManager
├── competitive_know_w1_issue123_20250617_143022  # KnowledgeWorker1
├── competitive_know_w2_issue123_20250617_143022  # KnowledgeWorker2
└── competitive_know_w3_issue123_20250617_143022  # KnowledgeWorker3
```

### 1.2 Git Worktree 管理システム

#### セットアップスクリプト
```bash
#!/bin/bash
# scripts/tmux_worktree_setup.sh

set -euo pipefail

ISSUE_ID=${1:-"default"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_DIR="/home/devuser/workspace"

echo "🏗️ tmux + git worktree セットアップ開始"
echo "Issue ID: $ISSUE_ID, Timestamp: $TIMESTAMP"

# 1. ディレクトリ構造作成
create_directory_structure() {
    local teams=("strategy_team" "execution_team" "review_team" "knowledge_rule_team")
    
    for team in "${teams[@]}"; do
        mkdir -p "worker/$team"
    done
    
    # 役割別ディレクトリ
    mkdir -p worker/strategy_team/{00.ProjectManager,01.PMOConsultant}
    mkdir -p worker/execution_team/{02.TaskExecutionManager,05.TaskExecutionWorker,08.TaskExecutionWorker,11.TaskExecutionWorker}
    mkdir -p worker/review_team/{03.TaskReviewManager,06.TaskReviewWorker,09.TaskReviewWorker,12.TaskReviewWorker}
    mkdir -p worker/knowledge_rule_team/{04.TaskKnowledgeRuleManager,07.TaskKnowledgeRuleWorker,10.TaskKnowledgeRuleWorker,13.TaskKnowledgeRuleWorker}
    
    echo "✅ ディレクトリ構造作成完了"
}

# 2. Git worktree作成
create_worktrees() {
    local role_mapping=(
        "worker/strategy_team/00.ProjectManager:pm"
        "worker/strategy_team/01.PMOConsultant:pmo"
        "worker/execution_team/02.TaskExecutionManager:exec_mgr"
        "worker/execution_team/05.TaskExecutionWorker:exec_w1"
        "worker/execution_team/08.TaskExecutionWorker:exec_w2"
        "worker/execution_team/11.TaskExecutionWorker:exec_w3"
        "worker/review_team/03.TaskReviewManager:rev_mgr"
        "worker/review_team/06.TaskReviewWorker:rev_w1"
        "worker/review_team/09.TaskReviewWorker:rev_w2"
        "worker/review_team/12.TaskReviewWorker:rev_w3"
        "worker/knowledge_rule_team/04.TaskKnowledgeRuleManager:know_mgr"
        "worker/knowledge_rule_team/07.TaskKnowledgeRuleWorker:know_w1"
        "worker/knowledge_rule_team/10.TaskKnowledgeRuleWorker:know_w2"
        "worker/knowledge_rule_team/13.TaskKnowledgeRuleWorker:know_w3"
    )
    
    for mapping in "${role_mapping[@]}"; do
        local dir_path=$(echo "$mapping" | cut -d: -f1)
        local role=$(echo "$mapping" | cut -d: -f2)
        local branch_name="competitive_${role}_${ISSUE_ID}_${TIMESTAMP}"
        
        # worktree作成
        git worktree add "$dir_path" -b "$branch_name"
        
        # 初期設定ファイル作成
        cat > "$dir_path/ROLE_CONFIG.md" << EOF
# Role Configuration

**Role**: $role
**Branch**: $branch_name
**Issue ID**: $ISSUE_ID
**Created**: $(date)
**Directory**: $dir_path

## 責任範囲
$(get_role_description "$role")

## 使用コマンド
\`\`\`bash
cd $dir_path
git status
git add . && git commit -m "Progress update"
git push origin $branch_name
\`\`\`
EOF
        
        echo "✅ Worktree作成: $dir_path -> $branch_name"
    done
}

# 3. 役割説明取得
get_role_description() {
    case "$1" in
        "pm") echo "プロジェクト全体の戦略決定・最終意思決定" ;;
        "pmo") echo "プロセス最適化・品質基準設定・リスク管理" ;;
        "exec_mgr") echo "実行戦略策定・Worker調整・進捗管理" ;;
        "exec_w1"|"exec_w2"|"exec_w3") echo "独立解決策実装・品質確保・成果報告" ;;
        "rev_mgr") echo "レビュー戦略・観点割当・統合評価" ;;
        "rev_w1"|"rev_w2"|"rev_w3") echo "専門観点レビュー・客観評価・改善提案" ;;
        "know_mgr") echo "ナレッジ戦略・体系化・品質管理" ;;
        "know_w1"|"know_w2"|"know_w3") echo "ナレッジ抽出・ルール化・文書化" ;;
        *) echo "未定義役割" ;;
    esac
}

# 実行
main() {
    cd "$BASE_DIR"
    create_directory_structure
    create_worktrees
    
    echo "🎯 セットアップ完了！"
    echo "次のステップ: ./scripts/tmux_session_start.sh --issue $ISSUE_ID"
}

main "$@"
```

#### ブランチ管理システム
```bash
#!/bin/bash
# scripts/competitive_branch_manager.sh

OPERATION=${1:-"list"}
ISSUE_ID=${2:-""}

case $OPERATION in
    "list")
        echo "📋 アクティブなcompetitiveブランチ:"
        git branch | grep "competitive_" | head -20
        ;;
    
    "status")
        echo "📊 Worktree状況:"
        git worktree list | grep "competitive_"
        ;;
        
    "sync")
        echo "🔄 全worktreeの同期実行:"
        for worktree in $(git worktree list | grep competitive_ | awk '{print $1}'); do
            echo "Syncing: $worktree"
            (cd "$worktree" && git pull origin main && git push origin HEAD)
        done
        ;;
        
    "clean")
        echo "🧹 完了したworktreeのクリーンアップ:"
        ./scripts/worktree_cleanup.sh --issue "$ISSUE_ID"
        ;;
        
    "merge")
        if [ -z "$ISSUE_ID" ]; then
            echo "Error: Issue ID required for merge operation"
            exit 1
        fi
        
        echo "🔀 Issue $ISSUE_ID の最終結果マージ:"
        # 採用決定されたworktreeをmainにマージ
        read -p "採用するworktreeのブランチ名を入力: " selected_branch
        git checkout main
        git merge --no-ff "$selected_branch" -m "Merge competitive solution for issue $ISSUE_ID"
        ;;
esac
```

## 2. tmux セッション管理仕様

### 2.1 セッション構造設計

#### マスターセッション構造
```bash
# セッション: competitive_framework
competitive_framework
├── Window 0: overview              # 全体管理・監視
├── Window 1: strategy             # 戦略チーム (2ペイン)
├── Window 2: execution            # 実行チーム (4ペイン)
├── Window 3: review               # レビューチーム (4ペイン)
├── Window 4: knowledge            # ナレッジチーム (4ペイン)
└── Window 5: monitoring           # 監視・ログ・メトリクス
```

#### 詳細ペイン配置
```bash
# Window 1: strategy (戦略)
strategy
├── Pane 0: 00.ProjectManager      [80x24]
└── Pane 1: 01.PMOConsultant       [80x24]

# Window 2: execution (実行)
execution
├── Pane 0: 02.TaskExecutionManager [40x12]
├── Pane 1: 05.TaskExecutionWorker  [40x12]
├── Pane 2: 08.TaskExecutionWorker  [40x12]
└── Pane 3: 11.TaskExecutionWorker  [40x12]

# Window 3: review (レビュー)
review
├── Pane 0: 03.TaskReviewManager    [40x12]
├── Pane 1: 06.TaskReviewWorker     [40x12]
├── Pane 2: 09.TaskReviewWorker     [40x12]
└── Pane 3: 12.TaskReviewWorker     [40x12]

# Window 4: knowledge (ナレッジ)
knowledge
├── Pane 0: 04.TaskKnowledgeRuleManager [40x12]
├── Pane 1: 07.TaskKnowledgeRuleWorker  [40x12]
├── Pane 2: 10.TaskKnowledgeRuleWorker  [40x12]
└── Pane 3: 13.TaskKnowledgeRuleWorker  [40x12]
```

### 2.2 セッション起動・管理システム

#### セッション起動スクリプト
```bash
#!/bin/bash
# scripts/tmux_session_start.sh

set -euo pipefail

ISSUE_ID=${1:-"default"}
SESSION_NAME="competitive_${ISSUE_ID}"

echo "🚀 tmux セッション起動: $SESSION_NAME"

# 1. メインセッション作成
tmux new-session -d -s "$SESSION_NAME" -n "overview"
tmux send-keys -t "$SESSION_NAME:overview" "echo '🎯 Competitive Framework - Issue: $ISSUE_ID'" Enter
tmux send-keys -t "$SESSION_NAME:overview" "echo '📊 Overview Dashboard Active'" Enter

# 2. 戦略ウィンドウ
tmux new-window -t "$SESSION_NAME" -n "strategy"
tmux split-window -h -t "$SESSION_NAME:strategy"

tmux send-keys -t "$SESSION_NAME:strategy.0" "cd worker/strategy_team/00.ProjectManager" Enter
tmux send-keys -t "$SESSION_NAME:strategy.0" "echo '🎯 ProjectManager - Issue: $ISSUE_ID'" Enter
tmux send-keys -t "$SESSION_NAME:strategy.0" "cat ROLE_CONFIG.md" Enter

tmux send-keys -t "$SESSION_NAME:strategy.1" "cd worker/strategy_team/01.PMOConsultant" Enter  
tmux send-keys -t "$SESSION_NAME:strategy.1" "echo '📋 PMOConsultant - Issue: $ISSUE_ID'" Enter
tmux send-keys -t "$SESSION_NAME:strategy.1" "cat ROLE_CONFIG.md" Enter

# 3. 実行ウィンドウ（4ペイン）
tmux new-window -t "$SESSION_NAME" -n "execution"
tmux split-window -h -t "$SESSION_NAME:execution"
tmux split-window -v -t "$SESSION_NAME:execution.0"
tmux split-window -v -t "$SESSION_NAME:execution.1"

# 実行チーム配置
local execution_dirs=(
    "worker/execution_team/02.TaskExecutionManager"
    "worker/execution_team/05.TaskExecutionWorker"
    "worker/execution_team/08.TaskExecutionWorker"
    "worker/execution_team/11.TaskExecutionWorker"
)

for i in "${!execution_dirs[@]}"; do
    tmux send-keys -t "$SESSION_NAME:execution.$i" "cd ${execution_dirs[$i]}" Enter
    tmux send-keys -t "$SESSION_NAME:execution.$i" "echo '⚡ Execution Worker $i - Issue: $ISSUE_ID'" Enter
    tmux send-keys -t "$SESSION_NAME:execution.$i" "cat ROLE_CONFIG.md" Enter
done

# 4. レビューウィンドウ（4ペイン）
tmux new-window -t "$SESSION_NAME" -n "review"
tmux split-window -h -t "$SESSION_NAME:review"
tmux split-window -v -t "$SESSION_NAME:review.0"
tmux split-window -v -t "$SESSION_NAME:review.1"

# レビューチーム配置
local review_dirs=(
    "worker/review_team/03.TaskReviewManager"
    "worker/review_team/06.TaskReviewWorker"
    "worker/review_team/09.TaskReviewWorker"
    "worker/review_team/12.TaskReviewWorker"
)

for i in "${!review_dirs[@]}"; do
    tmux send-keys -t "$SESSION_NAME:review.$i" "cd ${review_dirs[$i]}" Enter
    tmux send-keys -t "$SESSION_NAME:review.$i" "echo '🔍 Review Worker $i - Issue: $ISSUE_ID'" Enter
    tmux send-keys -t "$SESSION_NAME:review.$i" "cat ROLE_CONFIG.md" Enter
done

# 5. ナレッジウィンドウ（4ペイン）
tmux new-window -t "$SESSION_NAME" -n "knowledge"
tmux split-window -h -t "$SESSION_NAME:knowledge"
tmux split-window -v -t "$SESSION_NAME:knowledge.0"
tmux split-window -v -t "$SESSION_NAME:knowledge.1"

# ナレッジチーム配置
local knowledge_dirs=(
    "worker/knowledge_rule_team/04.TaskKnowledgeRuleManager"
    "worker/knowledge_rule_team/07.TaskKnowledgeRuleWorker"
    "worker/knowledge_rule_team/10.TaskKnowledgeRuleWorker"
    "worker/knowledge_rule_team/13.TaskKnowledgeRuleWorker"
)

for i in "${!knowledge_dirs[@]}"; do
    tmux send-keys -t "$SESSION_NAME:knowledge.$i" "cd ${knowledge_dirs[$i]}" Enter
    tmux send-keys -t "$SESSION_NAME:knowledge.$i" "echo '📚 Knowledge Worker $i - Issue: $ISSUE_ID'" Enter
    tmux send-keys -t "$SESSION_NAME:knowledge.$i" "cat ROLE_CONFIG.md" Enter
done

# 6. 監視ウィンドウ
tmux new-window -t "$SESSION_NAME" -n "monitoring"
tmux send-keys -t "$SESSION_NAME:monitoring" "echo '📊 System Monitoring - Issue: $ISSUE_ID'" Enter
tmux send-keys -t "$SESSION_NAME:monitoring" "watch -n 5 'git worktree list && echo && tmux list-sessions'" Enter

echo "✅ セッション起動完了: $SESSION_NAME"
echo "📱 接続コマンド: tmux attach-session -t $SESSION_NAME"
echo "🔄 各ウィンドウ: overview, strategy, execution, review, knowledge, monitoring"
```

#### セッション管理コマンド
```bash
#!/bin/bash
# scripts/tmux_session_manager.sh

OPERATION=${1:-"list"}
SESSION_NAME=${2:-"competitive_default"}

case $OPERATION in
    "list")
        echo "📋 アクティブセッション:"
        tmux list-sessions | grep competitive_
        ;;
        
    "status")
        echo "📊 セッション詳細: $SESSION_NAME"
        if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            tmux list-windows -t "$SESSION_NAME"
            echo ""
            tmux list-panes -t "$SESSION_NAME" -F "#{pane_index}: #{pane_title} [#{pane_width}x#{pane_height}]"
        else
            echo "セッション $SESSION_NAME は存在しません"
        fi
        ;;
        
    "broadcast")
        local message=${3:-"Hello from coordinator"}
        echo "📡 全ペインにメッセージ送信: $message"
        
        for window in overview strategy execution review knowledge monitoring; do
            tmux send-keys -t "$SESSION_NAME:$window" "echo '📡 BROADCAST: $message'" Enter
        done
        ;;
        
    "sync")
        echo "🔄 全ワーカーでgit status確認:"
        
        # 各ペインでgit statusを実行
        for window in strategy execution review knowledge; do
            tmux send-keys -t "$SESSION_NAME:$window" "git status" Enter
        done
        ;;
        
    "snapshot")
        local snapshot_dir="snapshots/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$snapshot_dir"
        
        echo "📸 セッション状態スナップショット: $snapshot_dir"
        
        # セッション情報保存
        tmux list-sessions > "$snapshot_dir/sessions.txt"
        tmux list-windows -t "$SESSION_NAME" > "$snapshot_dir/windows.txt"
        tmux list-panes -t "$SESSION_NAME" -F "#{pane_index}: #{pane_title} [#{pane_current_path}]" > "$snapshot_dir/panes.txt"
        
        # Git状態保存
        git worktree list > "$snapshot_dir/worktrees.txt"
        git branch | grep competitive_ > "$snapshot_dir/branches.txt"
        
        echo "✅ スナップショット保存完了: $snapshot_dir"
        ;;
esac
```

## 3. システム統合・自動化

### 3.1 統合ワークフロー自動化

#### 競争的実行フルサイクル
```bash
#!/bin/bash
# scripts/competitive_full_cycle.sh

set -euo pipefail

ISSUE_ID=$1
EXECUTION_TIME=${2:-"120"}  # 実行時間（分）
REVIEW_TIME=${3:-"60"}      # レビュー時間（分）

echo "🏁 競争的実行フルサイクル開始: Issue $ISSUE_ID"

# Phase 1: 環境セットアップ
echo "📋 Phase 1: 環境セットアップ (5分)"
./scripts/tmux_worktree_setup.sh "$ISSUE_ID"
./scripts/tmux_session_start.sh "$ISSUE_ID"

# Phase 2: 戦略策定
echo "🎯 Phase 2: 戦略策定 (15分)"
tmux send-keys -t "competitive_$ISSUE_ID:strategy.0" "echo 'ProjectManager: 戦略策定開始'" Enter
tmux send-keys -t "competitive_$ISSUE_ID:strategy.1" "echo 'PMOConsultant: プロセス設計開始'" Enter

sleep 900  # 15分待機

# Phase 3: 並列実行
echo "⚡ Phase 3: 並列実行 ($EXECUTION_TIME分)"
tmux send-keys -t "competitive_$ISSUE_ID:execution.0" "echo 'ExecutionManager: 実行開始指示'" Enter

# 各Workerに実行開始信号
for i in 1 2 3; do
    tmux send-keys -t "competitive_$ISSUE_ID:execution.$i" "echo 'Worker $i: 解決策実装開始'" Enter
    tmux send-keys -t "competitive_$ISSUE_ID:execution.$i" "git checkout -b solution_${i}_$(date +%H%M%S)" Enter
done

# 実行時間待機（定期チェック付き）
local elapsed=0
while [ $elapsed -lt $((EXECUTION_TIME * 60)) ]; do
    sleep 300  # 5分間隔
    elapsed=$((elapsed + 300))
    
    echo "📊 実行進捗: $((elapsed / 60))/$EXECUTION_TIME 分経過"
    
    # 進捗確認
    tmux send-keys -t "competitive_$ISSUE_ID:monitoring" "echo '進捗確認: $((elapsed / 60))分経過'" Enter
done

# Phase 4: レビュー実行
echo "🔍 Phase 4: レビュー実行 ($REVIEW_TIME分)"
tmux send-keys -t "competitive_$ISSUE_ID:review.0" "echo 'ReviewManager: レビュー開始'" Enter

# 各ReviewWorkerにレビュー開始指示
review_aspects=("技術評価" "UX評価" "セキュリティ評価")
for i in 1 2 3; do
    tmux send-keys -t "competitive_$ISSUE_ID:review.$i" "echo 'ReviewWorker $i: ${review_aspects[$((i-1))]}開始'" Enter
done

sleep $((REVIEW_TIME * 60))

# Phase 5: 統合評価・意思決定
echo "🏆 Phase 5: 統合評価・意思決定 (15分)"
tmux send-keys -t "competitive_$ISSUE_ID:strategy.0" "echo 'ProjectManager: 最終判定開始'" Enter

# 評価結果収集
./scripts/competitive_evaluation.py worker/execution_team/*/solution_*

# Phase 6: ナレッジ化
echo "📚 Phase 6: ナレッジ化 (30分)"
for i in 1 2 3; do
    tmux send-keys -t "competitive_$ISSUE_ID:knowledge.$i" "echo 'KnowledgeWorker $i: ナレッジ抽出開始'" Enter
done

sleep 1800  # 30分待機

echo "🎊 競争的実行フルサイクル完了: Issue $ISSUE_ID"
echo "📊 結果確認: tmux attach-session -t competitive_$ISSUE_ID"
```

### 3.2 リソース管理・パフォーマンス最適化

#### システムリソース監視
```bash
#!/bin/bash
# scripts/resource_monitor.sh

SESSION_NAME=${1:-"competitive_default"}
MONITOR_INTERVAL=${2:-30}

echo "📊 リソース監視開始: $SESSION_NAME (${MONITOR_INTERVAL}秒間隔)"

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU/メモリ使用量
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    mem_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
    
    # Git worktree数
    worktree_count=$(git worktree list | wc -l)
    
    # tmuxセッション数
    tmux_sessions=$(tmux list-sessions | wc -l)
    
    # ディスク使用量（workerディレクトリ）
    worker_disk=$(du -sh worker/ 2>/dev/null | cut -f1 || echo "N/A")
    
    echo "[$timestamp] CPU: ${cpu_usage}%, RAM: ${mem_usage}%, Worktrees: $worktree_count, Sessions: $tmux_sessions, Worker Disk: $worker_disk"
    
    # 警告レベルチェック
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        echo "⚠️ HIGH CPU USAGE: ${cpu_usage}%"
        tmux send-keys -t "$SESSION_NAME:monitoring" "echo 'WARNING: High CPU usage ${cpu_usage}%'" Enter
    fi
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        echo "⚠️ HIGH MEMORY USAGE: ${mem_usage}%"
        tmux send-keys -t "$SESSION_NAME:monitoring" "echo 'WARNING: High memory usage ${mem_usage}%'" Enter
    fi
    
    sleep $MONITOR_INTERVAL
done
```

#### 自動クリーンアップシステム
```bash
#!/bin/bash
# scripts/worktree_cleanup.sh

set -euo pipefail

ISSUE_ID=${1:-""}
FORCE_CLEAN=${2:-false}
RETENTION_DAYS=${3:-7}

echo "🧹 Worktree クリーンアップ開始"

if [ "$FORCE_CLEAN" = "--force-clean" ]; then
    echo "⚠️ 強制クリーンアップモード"
    FORCE_CLEAN=true
fi

# 1. 完了したIssueのworktree特定
if [ -n "$ISSUE_ID" ]; then
    echo "📋 特定Issue ($ISSUE_ID) のクリーンアップ"
    target_branches=$(git branch | grep "competitive_.*_${ISSUE_ID}_")
else
    echo "📋 古いworktreeの自動クリーンアップ (${RETENTION_DAYS}日以上)"
    # 7日以上古いブランチを対象
    cutoff_date=$(date -d "${RETENTION_DAYS} days ago" +%Y%m%d)
    target_branches=$(git branch | grep "competitive_" | awk -v cutoff="$cutoff_date" '
        {
            # ブランチ名から日付抽出 (competitive_role_issue_YYYYMMDD_HHMMSS)
            if (match($0, /competitive_.*_([0-9]{8})_/, arr)) {
                if (arr[1] < cutoff) print $0
            }
        }
    ')
fi

if [ -z "$target_branches" ]; then
    echo "✅ クリーンアップ対象のworktreeはありません"
    exit 0
fi

echo "🎯 クリーンアップ対象:"
echo "$target_branches"

if [ "$FORCE_CLEAN" != true ]; then
    read -p "上記のworktreeを削除しますか？ (y/N): " confirmation
    if [ "$confirmation" != "y" ] && [ "$confirmation" != "Y" ]; then
        echo "❌ クリーンアップをキャンセルしました"
        exit 0
    fi
fi

# 2. worktree削除実行
echo "$target_branches" | while read -r branch; do
    branch_name=$(echo "$branch" | sed 's/^[* ] //')
    
    if [ -z "$branch_name" ]; then
        continue
    fi
    
    echo "🗑️ 削除中: $branch_name"
    
    # worktreeパス特定
    worktree_path=$(git worktree list | grep "$branch_name" | awk '{print $1}' || echo "")
    
    if [ -n "$worktree_path" ] && [ -d "$worktree_path" ]; then
        # worktree削除
        git worktree remove "$worktree_path" --force
        echo "✅ Worktree削除: $worktree_path"
    fi
    
    # ブランチ削除
    git branch -D "$branch_name" 2>/dev/null || echo "⚠️ ブランチ削除失敗: $branch_name"
done

# 3. 空ディレクトリクリーンアップ
find worker/ -type d -empty -delete 2>/dev/null || true

echo "🎊 クリーンアップ完了"
echo "📊 残存worktree: $(git worktree list | wc -l)"
```

## 4. トラブルシューティング・メンテナンス

### 4.1 一般的問題の解決

#### システム診断スクリプト
```bash
#!/bin/bash
# scripts/system_diagnostics.sh

echo "🔧 tmux + git worktree システム診断"
echo "======================================"

# 1. 基本環境チェック
echo "📋 1. 基本環境"
echo "tmux version: $(tmux -V)"
echo "git version: $(git --version)"
echo "現在ディレクトリ: $(pwd)"
echo "ユーザー: $(whoami)"
echo ""

# 2. Git状態確認
echo "📋 2. Git状態"
echo "現在ブランチ: $(git branch --show-current)"
echo "Worktree数: $(git worktree list | wc -l)"
echo "Competitive ブランチ数: $(git branch | grep -c competitive_ || echo 0)"
echo ""

# 3. Tmux状態確認
echo "📋 3. Tmux状態"
echo "アクティブセッション数: $(tmux list-sessions 2>/dev/null | wc -l || echo 0)"
echo "Competitive セッション:"
tmux list-sessions 2>/dev/null | grep competitive_ || echo "  なし"
echo ""

# 4. ディスク容量確認
echo "📋 4. ディスク状況"
echo "Worker ディレクトリサイズ: $(du -sh worker/ 2>/dev/null | cut -f1 || echo 'N/A')"
echo "空きディスク容量: $(df -h . | tail -1 | awk '{print $4}')"
echo ""

# 5. プロセス確認
echo "📋 5. プロセス状況"
echo "Tmux プロセス数: $(ps aux | grep -c '[t]mux' || echo 0)"
echo "Git プロセス数: $(ps aux | grep -c '[g]it' || echo 0)"
echo ""

# 6. 問題検出
echo "📋 6. 問題検出"
problems=0

# Git worktree整合性チェック
if git worktree list | grep -q "missing"; then
    echo "⚠️ 破損したworktreeが検出されました"
    problems=$((problems + 1))
fi

# Tmuxゾンビセッションチェック
zombie_sessions=$(tmux list-sessions 2>/dev/null | grep -c "no server running" || echo 0)
if [ "$zombie_sessions" -gt 0 ]; then
    echo "⚠️ ゾンビtmuxセッションが検出されました: $zombie_sessions"
    problems=$((problems + 1))
fi

# ディスク容量チェック
available_gb=$(df . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$available_gb" -lt 5 ]; then
    echo "⚠️ ディスク容量不足: ${available_gb}GB残り"
    problems=$((problems + 1))
fi

if [ $problems -eq 0 ]; then
    echo "✅ 問題は検出されませんでした"
else
    echo "❌ $problems 個の問題が検出されました"
    echo ""
    echo "🔧 推奨アクション:"
    echo "1. 自動修復実行: ./scripts/system_repair.sh"
    echo "2. 手動クリーンアップ: ./scripts/worktree_cleanup.sh --force-clean"
    echo "3. システム再起動: ./scripts/system_restart.sh"
fi
```

#### 自動修復システム
```bash
#!/bin/bash
# scripts/system_repair.sh

echo "🔧 システム自動修復開始"

# 1. 破損worktree修復
echo "📋 1. 破損worktree修復"
git worktree list | grep "missing" | while read -r line; do
    path=$(echo "$line" | awk '{print $1}')
    echo "🔧 修復中: $path"
    git worktree remove "$path" --force
done

# 2. ゾンビtmuxセッション削除
echo "📋 2. ゾンビセッション削除"
tmux kill-server 2>/dev/null || echo "tmuxサーバーなし"

# 3. 孤立ディレクトリ削除
echo "📋 3. 孤立ディレクトリ削除"
find worker/ -type d -empty -delete 2>/dev/null || true

# 4. Git整合性確認
echo "📋 4. Git整合性確認"
git fsck --no-progress

echo "✅ システム修復完了"
```

### 4.2 パフォーマンス最適化

#### 設定最適化
```bash
# ~/.tmux.conf に追加する最適化設定
# tmux設定最適化（competitive environment用）

# セッション管理最適化
set -g base-index 1
set -g pane-base-index 1
set -g renumber-windows on

# パフォーマンス最適化
set -g history-limit 50000
set -g display-time 2000
set -g status-interval 5
set -sg escape-time 1

# 大量ペイン対応
set -g status-bg colour234
set -g status-fg colour137
set -g window-status-current-bg colour238
set -g window-status-current-fg colour81

# Competitive環境専用キーバインド
bind-key C-c new-session -d -s "competitive_$(date +%m%d_%H%M)"
bind-key C-w list-sessions \; command-prompt "attach-session -t %%"
bind-key C-r source-file ~/.tmux.conf \; display-message "Config reloaded"

# パネル間移動最適化
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# 監視モード
bind-key M-m new-window -n "monitoring" \; send-keys "watch -n 5 'git worktree list && echo && tmux list-sessions'" Enter
```

## まとめ：技術基盤の確立

### 実現された技術価値
1. **完全分離**: git worktreeによる独立開発環境
2. **並列効率**: tmux多重実行による同時作業
3. **自動化**: セットアップ・管理・クリーンアップの自動化
4. **監視**: リアルタイム状況把握・問題検出

### 運用上の優位性
- **スケーラビリティ**: Worker数の動的調整対応
- **信頼性**: 自動診断・修復システム
- **効率性**: ワンクリック環境構築
- **保守性**: 統合管理・監視システム

この技術仕様により、コンペ方式組織活動の技術基盤が確立され、安定的で効率的な並列開発環境が実現されました。