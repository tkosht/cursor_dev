#!/bin/bash
# Auto task report wrapper - Stop hook用
# 組織状態がアクティブな場合のみ実行

# 組織状態確認
if [[ -f "/home/devuser/workspace/.claude/organization_state.json" ]] && \
   [[ "$(jq -r '.active' /home/devuser/workspace/.claude/organization_state.json 2>/dev/null || echo 'false')" == "true" ]]; then
    # auto_task_report_v2.shを実行
    /home/devuser/workspace/.claude/hooks/auto_task_report_v2.sh
fi