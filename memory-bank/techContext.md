# 技術コンテキスト

## 開発環境
- Python 3.10～3.12
- Poetry による依存関係管理
- flake8 によるコード品質管理
- pytest によるテスト自動化

## 主要技術スタック
1. データ取得
   - Twitter API v2
   - Selenium/Playwright（ブラウザ自動化）
   - aiohttp（非同期HTTP通信）

2. 検索エンジン
   - Faiss/Pinecone（ベクトルDB）
   - Elasticsearch（キーワード検索）
   - sentence-transformers（Embedding生成）

3. LLM統合
   - Gemini 2.0 Flash API
   - OpenAI API
   - Anthropic Claude API
   - Ollama API

4. フロントエンド
   - Gradio
   - HTML/CSS
   - JavaScript

## 技術的制約
1. パフォーマンス要件
   - 検索レイテンシ: 3秒以内
   - LLM応答時間: 10秒以内
   - メモリ使用量: 4GB以内

2. スケーラビリティ
   - ブックマーク数: 〜100,000件
   - 同時ユーザー数: 1ユーザー
   - ストレージ容量: 〜10GB

3. 依存関係
   - Python 3.10以上必須
   - CUDA対応GPU（オプション）
   - 最小8GBメモリ

## セキュリティ要件
1. 認証・認可
   - Twitter OAuth2.0
   - LLM APIキー管理
   - 環境変数による機密情報管理

2. データ保護
   - ローカルストレージのみ
   - 暗号化不要
   - バックアップ任意

## 開発プラクティス
1. コーディング規約
   - Google Style Python Docstrings
   - Type Hints 必須
   - 行長制限: 79文字
   - インデント: 4スペース

2. テスト要件
   - Unit Tests: カバレッジ80%以上
   - Integration Tests: 主要フロー
   - E2E Tests: 重要ユースケース

3. CI/CD
   - GitHub Actions
   - 自動テスト
   - Lint チェック
   - 依存関係チェック 