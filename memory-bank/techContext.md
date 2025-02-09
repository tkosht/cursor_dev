# 技術コンテキスト

## 開発環境
1. VSCode Dev Container環境
   - ベースイメージ: python:3.12-slim
   - 作業ディレクトリ: ~/workspace
   - 公開ポート: 7860（Gradio用）
   - コンテナ設定は.devcontainerで管理
   - Dockerfileは不要であり、既に削除済み（新規Dockerfile作成は禁止）

2. Python環境
   - バージョン: 3.10～3.12
   - 依存関係管理: Poetry
   - 仮想環境: 無効（Dev Container内のため）
   - flake8, black, isort, pytest を使用

3. セキュリティ
   - 機密情報は環境変数で管理
   - .envファイルは.gitignoreに追加
   - APIキーは.devcontainer経由で管理
   - コンテナ内での機密情報管理を徹底

## 使用技術
1. LLM
   - Gemini 2.0 Flash
   - Google Cloud API

2. ベクトルDB
   - Faiss
   - インメモリ検索

3. フロントエンド
   - Gradio UI
   - ポート7860で公開

## 技術的制約
1. 開発環境
   - VSCode Dev Container環境での開発必須
   - コンテナ外での開発は不可
   - .devcontainer設定の変更は慎重に

2. 依存関係
   - Poetryでの管理必須
   - バージョン固定
   - 最小限の依存関係

3. セキュリティ
   - 機密情報の直接コミット禁止
   - 環境変数経由での管理必須
   - コンテナ内でのセキュリティ確保

## 依存関係
1. 必須パッケージ
   - google-cloud-aiplatform
   - faiss-cpu
   - gradio
   - python-dotenv

2. 開発用パッケージ
   - flake8
   - black
   - isort
   - pytest

3. CI/CD
   - GitHub Actions
   - Docker Hub 