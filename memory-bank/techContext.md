# 技術コンテキスト

## 開発環境
- Python 3.10～3.12
- VSCode Dev Container
- poetry による依存関係管理（pipは使用禁止）
- GitHub Actions による CI/CD

## 主要ライブラリ

### 実装済み
1. **Twitter API関連**
   - aiohttp: 非同期HTTPクライアント
   - python-dotenv: 環境変数管理

2. **検索エンジン**
   - faiss-cpu: ベクトル検索
   - sentence-transformers: テキスト埋め込み
   - numpy: 数値計算

3. **LLM統合**
   - google.generativeai: Gemini API
   - openai: GPT API
   - anthropic: Claude API
   - ollama: ローカルLLM

4. **UI**
   - gradio: Webインターフェース
   - markdown: マークダウン処理

### 今後追加予定
1. **パフォーマンス最適化**
   - redis: キャッシュ
   - celery: 非同期タスク
   - prometheus-client: メトリクス

2. **モニタリング**
   - structlog: 構造化ログ
   - sentry-sdk: エラー監視
   - opentelemetry: 分散トレーシング

## 技術的制約

### 現状の制約
1. **TwitterAPI**
   - レート制限: 15分/180リクエスト
   - ブックマーク取得上限: 800件
   - OAuth認証必須

2. **検索エンジン**
   - メモリ使用量の制限
   - インデックスサイズの制限
   - 検索精度とパフォーマンスのトレードオフ

3. **LLM**
   - API呼び出しコスト
   - レイテンシ
   - トークン制限

4. **UI**
   - 非同期処理の制限
   - レスポンシブ対応
   - ブラウザ互換性

### 対応策
1. **TwitterAPI対応**
   - キャッシュ導入
   - バッチ処理
   - リトライ機構

2. **検索エンジン最適化**
   - インデックスの分割
   - キャッシュ戦略
   - 検索パラメータのチューニング

3. **LLM最適化**
   - プロンプト最適化
   - コンテキスト管理
   - モデル切替機能

4. **UI改善**
   - 非同期ローディング
   - エラーハンドリング
   - レスポンシブ対応

## パフォーマンス要件

### 目標値
1. **レスポンス時間**
   - 検索: 1秒以内
   - LLM応答: 5秒以内
   - UI更新: 100ms以内

2. **スループット**
   - 同時ユーザー: 10人
   - 検索クエリ: 10 QPS
   - ブックマーク更新: 1回/分

3. **リソース使用**
   - メモリ: 2GB以内
   - CPU: 2コア相当
   - ストレージ: 10GB以内

### モニタリング項目
1. **アプリケーション**
   - API応答時間
   - エラーレート
   - 検索精度

2. **インフラ**
   - メモリ使用量
   - CPU使用率
   - ディスクI/O

## セキュリティ要件

### 実装済み
1. **認証**
   - 環境変数による認証情報管理
   - APIキーの安全な取り扱い

2. **データ保護**
   - ローカルデータの暗号化
   - セキュアな通信

### 実装予定
1. **入力検証**
   - XSS対策
   - SQLインジェクション対策
   - 入力サニタイズ

2. **アクセス制御**
   - レート制限
   - IPフィルタリング
   - ユーザー認証

## 依存関係（poetry管理）
1. 必須パッケージ（poetry add）
   - google-cloud-aiplatform
   - faiss-cpu
   - gradio
   - python-dotenv

2. 開発用パッケージ（poetry add --group dev）
   - flake8
   - black
   - isort
   - pytest
   - psutil

3. CI/CD
   - GitHub Actions
   - Docker Hub 