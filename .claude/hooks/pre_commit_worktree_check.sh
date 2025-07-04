#!/bin/bash
# git commit前のworktreeチェックスクリプト
# PreToolUse hook で git commit 前に実行

source "/home/devuser/workspace/.claude/hooks/tmux_organization_utils.sh"

# 組織活動文脈の確認
if ! is_organization_context; then
    exit 0  # 通常の作業では何もしない
fi

# 現在のペイン情報を取得
get_current_pane_info

# git環境でない場合はスキップ
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    exit 0
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
WORK_DIR=$(pwd)

# 競争的ブランチでのコミット前チェック
if is_competitive_branch; then
    log_organization_activity "PRE_COMMIT_CHECK: Performing competitive branch commit checks"
    
    # ブランチ命名規則の確認
    if [[ ! "$CURRENT_BRANCH" =~ competitive_[a-zA-Z_]+_[a-zA-Z0-9_]+_[0-9]{8}_[0-9]{6} ]]; then
        echo "⚠️ WARNING: Branch naming does not follow competitive convention"
        echo "Expected pattern: competitive_{role}_{issue_id}_{timestamp}"
        echo "Current branch: $CURRENT_BRANCH"
        
        # ProjectManagerに警告を送信
        PM_PANE=$(find_project_manager_pane)
        if [[ -n "$PM_PANE" ]]; then
            send_tmux_message "$PM_PANE" "⚠️ NAMING WARNING: Branch '$CURRENT_BRANCH' in pane-$CURRENT_PANE does not follow competitive naming convention"
        fi
    fi
    
    # worktreeディレクトリ内での作業確認
    if [[ "$WORK_DIR" =~ /worker/ ]]; then
        echo "✅ Working in designated worktree directory"
        log_organization_activity "PRE_COMMIT_CHECK: Confirmed working in worktree directory"
    else
        echo "⚠️ WARNING: Not working in designated worktree directory"
        echo "Current directory: $WORK_DIR"
        echo "Expected: */worker/*"
        
        # ProjectManagerに通知
        PM_PANE=$(find_project_manager_pane)
        if [[ -n "$PM_PANE" ]]; then
            send_tmux_message "$PM_PANE" "⚠️ DIRECTORY WARNING: pane-$CURRENT_PANE working outside worktree directory: $WORK_DIR"
        fi
    fi
    
    # staging areaの内容確認
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null | wc -l)
    if [[ "$STAGED_FILES" -eq 0 ]]; then
        echo "⚠️ WARNING: No files staged for commit"
        exit 2  # コミットをブロック
    fi
    
    # 大きなファイルの確認
    LARGE_FILES=$(git diff --cached --name-only | xargs -r ls -la 2>/dev/null | awk '$5 > 1048576 {print $9 " (" $5 " bytes)"}')
    if [[ -n "$LARGE_FILES" ]]; then
        echo "⚠️ WARNING: Large files detected in commit:"
        echo "$LARGE_FILES"
        
        # ProjectManagerに通知
        PM_PANE=$(find_project_manager_pane)
        if [[ -n "$PM_PANE" ]]; then
            send_tmux_message "$PM_PANE" "⚠️ LARGE FILES: pane-$CURRENT_PANE attempting to commit large files on branch '$CURRENT_BRANCH'"
        fi
    fi
    
    echo "✅ Competitive branch commit checks completed"
else
    # 非競争的ブランチでのmainブランチチェック
    if [[ "$CURRENT_BRANCH" =~ ^(main|master)$ ]]; then
        echo "🚨 WARNING: Committing directly to $CURRENT_BRANCH"
        echo "Consider creating a feature branch for competitive development"
        
        # ProjectManagerに警告
        PM_PANE=$(find_project_manager_pane)
        if [[ -n "$PM_PANE" ]]; then
            send_tmux_message "$PM_PANE" "🚨 MAIN BRANCH COMMIT: pane-$CURRENT_PANE committing directly to '$CURRENT_BRANCH'"
        fi
    fi
fi

log_organization_activity "PRE_COMMIT_CHECK: Completed pre-commit checks for branch '$CURRENT_BRANCH'"