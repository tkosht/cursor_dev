# APIキー設定ガイド

このドキュメントでは、Gemini A2Aエージェントで使用するAPIキーの設定方法について詳しく説明します。

## 🔑 必要なAPIキー

### Google Gemini API キー

**必須**: Google Gemini 2.5 Pro API を使用するために必要です。

#### 取得方法
1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. "Create API Key" をクリック
4. 生成されたAPIキーをコピー

## 📝 設定方法

### 方法1: .envファイル使用（推奨）

#### 手順
```bash
# 1. プロジェクトルートで.env.exampleをコピー
cp .env.example .env

# 2. .envファイルを編集
nano .env  # または vim, code 等
```

#### .envファイルの設定例
```bash
# Required: Google Gemini API Key
GEMINI_API_KEY=AIzaSyD...your-actual-api-key-here

# Optional: 設定をカスタマイズ
GEMINI_MODEL=gemini-2.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000
```

#### 利点
- ✅ プロジェクト固有の設定
- ✅ Git管理外（.gitignoreで除外済み）
- ✅ 環境間の切り替えが容易

### 方法2: 環境変数設定

#### 一時的な設定（セッション中のみ）
```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

#### 永続的な設定
```bash
# bash使用の場合
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# zsh使用の場合
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 方法3: Docker Compose環境変数

Dev Container使用時は、compose.ymlで環境変数を渡すことも可能です：

```yaml
# compose.yml（例）
services:
  app:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

## ✅ 設定確認

### APIキーの確認
```bash
# 1. 環境変数の確認
echo $GEMINI_API_KEY

# 2. エージェント起動テスト
python scripts/run_gemini_agent.py
```

### 期待される出力
```
🚀 Starting gemini-chat-agent...
📡 URL: http://localhost:8004
🧠 Model: gemini-2.5-pro
🌡️ Temperature: 0.7
💡 Test at: http://localhost:8004/.well-known/agent.json
📊 Health check: http://localhost:8004/health

💬 Ready for A2A conversations!
✅ Gemini API connection verified
```

## 🛠️ トラブルシューティング

### エラー: "GEMINI_API_KEY environment variable is required"

**原因**: APIキーが設定されていない

**解決方法**:
1. .envファイルにAPIキーを設定
2. 環境変数としてAPIキーを設定
3. APIキーの形式を確認（AIzaSy で始まる）

### エラー: "API key appears to be invalid"

**原因**: APIキーの形式が不正

**解決方法**:
1. APIキーを再生成
2. 形式を確認（通常 39文字、AIzaSy で始まる）
3. 余分な空白や改行を除去

### エラー: "Failed to initialize Gemini client"

**原因**: APIキーは有効だが、API接続に問題

**解決方法**:
1. ネットワーク接続を確認
2. APIキーの権限を確認
3. Google AI APIが有効になっているか確認

## 🔒 セキュリティ注意事項

### 機密情報の保護
- ❌ APIキーをソースコードに直接記述しない
- ❌ APIキーをGitリポジトリにコミットしない
- ✅ .envファイルを使用（.gitignoreで除外済み）
- ✅ 環境変数で管理

### APIキーの管理
- 定期的にAPIキーを更新
- 不要になったAPIキーは削除
- チーム間でのAPIキー共有は適切な方法で実施

## 📋 設定可能な環境変数

| 環境変数名 | 必須 | デフォルト値 | 説明 |
|-----------|------|-------------|------|
| `GEMINI_API_KEY` | ✅ | なし | Google Gemini API キー |
| `GEMINI_MODEL` | ❌ | `gemini-2.5-pro-preview-05-06 | 使用するGeminiモデル |
| `GEMINI_TEMPERATURE` | ❌ | `0.7` | 創造性パラメータ (0.0-1.0) |
| `GEMINI_MAX_TOKENS` | ❌ | `1000` | 最大出力トークン数 |
| `A2A_AGENT_PORT` | ❌ | `8004` | エージェントのポート番号 |
| `DEBUG_MODE` | ❌ | `false` | デバッグモード有効化 |

---

**作成日**: 2025-01-XX  
**更新日**: 2025-01-XX 