#!/bin/bash
# Pre-commit worktree check wrapper - PreToolUse hook用
# git commit実行前に組織状態を確認

# 組織状態確認
if [[ -f "/home/devuser/workspace/.claude/organization_state.json" ]] && \
   [[ "$(jq -r '.active' /home/devuser/workspace/.claude/organization_state.json 2>/dev/null || echo 'false')" == "true" ]] && \
   [[ "$TOOL_INPUT_COMMAND" =~ 'git commit' ]]; then
    # pre_commit_worktree_check.shを実行
    /home/devuser/workspace/.claude/hooks/pre_commit_worktree_check.sh
fi