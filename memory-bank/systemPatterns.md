# システムパターン

## アーキテクチャパターン
1. レイヤードアーキテクチャ
   - プレゼンテーション層（Gradio UI）
   - アプリケーション層（ビジネスロジック）
   - インフラストラクチャ層（外部サービス連携）

2. クリーンアーキテクチャ
   - 依存関係の方向は内側に向かう
   - インターフェースによる疎結合
   - ドメインロジックの独立性確保

3. 開発環境パターン
   - VSCode Dev Container開発
   - コンテナ設定の一元管理
   - 環境の再現性確保

## 設計パターン
1. Factory Pattern
   - LLMクライアントの生成
   - ベクトルDBの初期化
   - UIコンポーネントの生成

2. Repository Pattern
   - ブックマークデータの永続化
   - 検索インデックスの管理
   - 設定情報の管理

3. Strategy Pattern
   - 検索アルゴリズムの切り替え
   - LLMプロバイダーの切り替え
   - UIテーマの切り替え

## 実装パターン
1. 依存関係管理
   - Poetry使用
   - バージョン固定
   - 最小限の依存関係

2. コード品質管理
   - flake8によるLint
   - blackによるフォーマット
   - isortによるimport整理

3. テストパターン
   - pytestによるテスト実装
   - カバレッジ80%以上
   - テストピラミッドの適用

## 統合パターン
1. 外部サービス連携
   - Google Cloud API
   - Twitter API
   - ベクトルDB

2. 非同期処理
   - async/await
   - バックグラウンドタスク
   - キャッシュ戦略

3. エラーハンドリング
   - 例外の階層化
   - ログ出力の標準化
   - リトライ戦略

## 開発プラクティス
1. コーディング規約
   - Google Style Python Docstrings
   - Type Hints必須
   - 行長制限79文字
   - インデント4スペース

2. バージョン管理
   - Git Flow
   - コミットメッセージ規約
   - PRレビュー必須

3. CI/CD
   - GitHub Actions
   - 自動テスト
   - コード品質チェック

## 主要コンポーネント
1. データ取得層
   - TwitterAPI連携
   - ブラウザ自動化
   - ポーリング管理

2. 検索エンジン層
   - ベクトルデータベース
   - キーワードインデックス
   - ハイブリッド検索

3. LLM処理層
   - マルチバックエンド対応
   - プロンプト管理
   - コンテキスト制御

4. UI層
   - Gradioインターフェース
   - 検索・フィルタリング
   - 結果表示

## データフロー
1. ブックマーク取得
   ```mermaid
   sequenceDiagram
       Controller->>BookmarkFetcher: 取得要求
       BookmarkFetcher->>TwitterAPI: API呼び出し
       TwitterAPI-->>BookmarkFetcher: ブックマークデータ
       BookmarkFetcher->>SearchEngine: インデックス更新
   ```

2. 検索処理
   ```mermaid
   sequenceDiagram
       UI->>Controller: 検索クエリ
       Controller->>SearchEngine: 検索実行
       SearchEngine->>VectorDB: ベクトル検索
       SearchEngine->>KeywordIndex: キーワード検索
       SearchEngine-->>Controller: 統合結果
       Controller->>LLMProcessor: 回答生成
       LLMProcessor-->>UI: 結果表示
   ``` 