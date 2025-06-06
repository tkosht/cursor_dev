# A2Aエージェント開発 クイックセットアップガイド

このガイドでは、A2Aエージェントの開発環境を最短でセットアップする手順を説明します。

## 前提条件

- **OS**: Windows 10/11, macOS 10.15以降, Ubuntu 20.04以降
- **Python**: 3.10, 3.11, または 3.12
- **Git**: インストール済み
- **メモリ**: 4GB以上推奨

## セットアップ手順

### 1. リポジトリのクローン

```bash
# GitHubからクローン
git clone https://github.com/tkosht/cursor_dev.git
cd cursor_dev

# または、テンプレートから新規作成
git clone https://github.com/tkosht/cursor_dev.git my-a2a-project
cd my-a2a-project
rm -rf .git
git init
```

### 2. Python環境のセットアップ

#### Option A: Poetry を使用（推奨）

```bash
# Poetryのインストール（未インストールの場合）
curl -sSL https://install.python-poetry.org | python3 -

# 依存関係のインストール
poetry install

# 仮想環境に入る
poetry shell
```

#### Option B: venv を使用

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. 動作確認

```bash
# 品質チェックの実行
python scripts/quality_gate_check.py

# テストの実行
pytest --cov=app --cov-report=html

# カバレッジレポートの確認
# Windows
start output/coverage/html/index.html
# macOS
open output/coverage/html/index.html
# Linux
xdg-open output/coverage/html/index.html
```

### 4. サーバーの起動

```bash
# 開発サーバーの起動
uvicorn app.a2a.server.app:app --reload

# ブラウザで確認
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/agent (エージェント情報)
```

## Docker環境（オプション）

### Docker環境のセットアップ

```bash
# Docker環境の起動
make up

# コンテナ内でのコマンド実行
make bash
# コンテナ内で
pytest --cov=app
python scripts/quality_gate_check.py

# 環境のクリーンアップ
make clean
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. Poetryが見つからない

```bash
# パスを通す
export PATH="$HOME/.local/bin:$PATH"
# または .bashrc/.zshrc に追加
```

#### 2. Python バージョンエラー

```bash
# pyenvを使用してPython 3.10をインストール
pyenv install 3.10.13
pyenv local 3.10.13
```

#### 3. 依存関係のインストールエラー

```bash
# キャッシュをクリアして再試行
poetry cache clear pypi --all
poetry install
```

#### 4. ポート8000が使用中

```bash
# 別のポートで起動
uvicorn app.a2a.server.app:app --reload --port 8001
```

#### 5. Gitフックエラー

```bash
# Gitフックの権限を修正
chmod +x .git/hooks/*

# または一時的に無効化
git commit --no-verify
```

## 次のステップ

1. **初心者の方**: [A2Aプロトコル入門](note_a2a_introduction_level1.md)を読む
2. **実装を始める方**: [A2A実践ガイド](note_a2a_practice_level2.md)を参照
3. **本格運用を検討**: [エンタープライズA2A](note_a2a_advanced_level3.md)を確認

## サポート

- **Issues**: [GitHub Issues](https://github.com/tkosht/cursor_dev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tkosht/cursor_dev/discussions)
- **Wiki**: [プロジェクトWiki](https://github.com/tkosht/cursor_dev/wiki)