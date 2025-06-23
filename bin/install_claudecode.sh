#!/usr/bin/sh

# --- 1. nvmのインストールと有効化 ---
curl -sSL -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # nvmをロードする推奨方法

# --- 2. Node.jsのインストールと使用 ---
# 最新のLTS(長期サポート)版をインストールし、現在のセッションで使用する
# 'nvm use'も内部的に実行されるため、別途'use'コマンドは不要
nvm install --lts

# --- 3. プロジェクトの依存関係をインストール ---
# これはプロジェクトのローカルパッケージなので変更なし
npm install

# --- 4. グローバルパッケージのインストール ---
# nvmが管理する場所にClaude Codeをグローバルインストールする
echo "Installing @anthropic-ai/claude-code globally..."
npm install -g @anthropic-ai/claude-code

# --- 5. MCP追加スクリプトの実行 ---
sh bin/add_cognee_mcp.sh


echo "Installation complete."

