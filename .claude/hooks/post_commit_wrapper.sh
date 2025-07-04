#!/bin/sh
# Post commit merge request wrapper - JSON stdin処理
# PostToolUse hook で Bash(git commit) 成功後に実行

# JSON入力をstdinから読み取り
JSON_INPUT=$(cat)

# ツール名とコマンドを抽出
TOOL_NAME=$(echo "$JSON_INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$JSON_INPUT" | jq -r '.tool_input.command // empty')

# Bashツールかつgit commitコマンドの場合のみ処理
if [ "$TOOL_NAME" = "Bash" ]; then
    case "$COMMAND" in
        *git*commit*)
            # 組織状態確認
            if [ -f "/home/devuser/workspace/.claude/organization_state.json" ] && \
               [ "$(jq -r '.active' /home/devuser/workspace/.claude/organization_state.json 2>/dev/null || echo 'false')" = "true" ]; then
                # 既存のスクリプトを呼び出し（組織コンテキスト環境変数を設定）
                TMUX_ORGANIZATION_CONTEXT=true TMUX="$TMUX" /home/devuser/workspace/.claude/hooks/post_commit_merge_request.sh
            fi
            ;;
    esac
fi