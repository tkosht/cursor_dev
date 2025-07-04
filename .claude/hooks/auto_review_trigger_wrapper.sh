#!/bin/sh
# Auto review trigger wrapper - JSON stdin処理
# PostToolUse hook で Write|Edit|MultiEdit 後に実行

# JSON入力をstdinから読み取り
JSON_INPUT=$(cat)

# ツール名とファイルパスを抽出
TOOL_NAME=$(echo "$JSON_INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$JSON_INPUT" | jq -r '.tool_input.file_path // empty')

# Write/Edit/MultiEditツールかつファイルパスが存在する場合のみ処理
case "$TOOL_NAME" in
    Write|Edit|MultiEdit)
        if [ -n "$FILE_PATH" ] && [ -f "$FILE_PATH" ]; then
            # ファイル拡張子チェック
            case "$FILE_PATH" in
                *.md|*.py|*.js|*.ts|*.json|*.yaml|*.yml)
                    # 組織状態確認
                    if [ -f "/home/devuser/workspace/.claude/organization_state.json" ] && \
                       [ "$(jq -r '.active' /home/devuser/workspace/.claude/organization_state.json 2>/dev/null || echo 'false')" = "true" ]; then
                        # シンプル版スクリプトを呼び出し（Team4組織活動特化）
                        /home/devuser/workspace/.claude/hooks/auto_review_trigger_simple.sh "$FILE_PATH" "$TMUX_PANE"
                    fi
                    ;;
            esac
        fi
        ;;
esac