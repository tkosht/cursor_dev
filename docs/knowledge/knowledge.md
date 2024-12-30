# 知識ベース

## 非同期処理
### リクエスト制御
1. 同時実行数の制御
   - Semaphoreを使用して同時実行数を制限
   - リクエスト間隔にバッファを設けることで安定性を確保
   - 理論上の最大スループットよりも余裕を持った設定が重要
   - 実装例: implementation_patterns.md の RequestControllerパターン を参照

2. セッション管理
   - セッションの生存期間を明確に管理
   - 再利用可能なセッションは維持し、一時的なセッションは確実にクローズ
   - コンテキストマネージャを活用した安全なリソース管理
   - 実装例: implementation_patterns.md の SessionManagerパターン を参照

3. エラーハンドリング
   - タイムアウト、ネットワークエラー、レート制限を個別に処理
   - エラー情報を詳細に記録し、再試行戦略に活用
   - カスタム例外を使用して意味のある情報を伝達
   - 実装例: implementation_patterns.md の ErrorHandlerパターン を参照

### パフォーマンスチューニング
1. リクエスト間隔の最適化
   - 理論値の50%程度を基準に設定（`1.0 / (max_concurrent_requests * 0.5)`）
   - スリープ時間にバッファ（0.2-0.3秒）を追加
   - 実行環境に応じて調整可能な設計
   - 実装例: implementation_patterns.md の RequestControllerパターン を参照

2. スループット制御
   - 同時実行数とリクエスト間隔のバランスを取る
   - モニタリングによる実際のスループット測定
   - 安定性を優先した制限値の設定
   - 実装例: implementation_patterns.md の AsyncTestCaseパターン のパフォーマンステスト部分を参照

## ドメイン管理
### フィルタリング戦略
1. 基本ポリシー
   - 同一ドメインは常に許可
   - 明示的に許可されたドメインのみアクセス可能
   - サブドメインの扱いを明確に定義
   - 実装例: implementation_patterns.md の DomainFilterパターン を参照

2. 設定の柔軟性
   - デフォルトは制限的な設定
   - 必要に応じて許可ドメインを追加可能
   - テスト環境用の特別な許可設定（例：test.local）
   - 実装例: implementation_patterns.md の ConfigurationManagerパターン を参照

## テスト設計
### カバレッジ戦略
1. 優先順位付け
   - コアロジックを最優先（90%以上）
   - エラーハンドリングを重視（80%以上）
   - ユーティリティ機能は状況に応じて（50%以上）
   - 実装例: implementation_patterns.md の AsyncTestCaseパターン を参照

2. テストケース設計
   - 正常系と異常系の両方をカバー
   - エッジケースの網羅的なテスト
   - パフォーマンス要件の検証
   - 実装例: implementation_patterns.md の AsyncTestCaseパターン を参照

### 非同期テスト
1. テスト環境構築
   - モックサーバーの活用
   - 実際のネットワーク動作のシミュレーション
   - タイミングに依存しない安定したテスト
   - 実装例: implementation_patterns.md の AsyncTestServerパターン を参照

2. 警告への対応
   - GeneratorExit等の非同期処理特有の警告を理解
   - クリーンアップ処理の適切な実装
   - テストフレームワークとの互換性確保
   - 実装例: implementation_patterns.md の AsyncTestServerパターン の __aexit__ メソッドを参照

## 実装のベストプラクティス
### コード品質
1. 複雑度の管理
   - メソッドの責務を明確に分離
   - 条件分岐を最小限に抑制
   - ヘルパー関数の適切な活用
   - 実装例: implementation_patterns.md の各パターンのメソッド分割を参照

2. エラー処理
   - カスタム例外クラスの階層化
   - エラーメッセージの標準化
   - ログ出力とモニタリングの連携
   - 実装例: implementation_patterns.md の ErrorHandlerパターン を参照

### パフォーマンス最適化
1. リソース管理
   - コネクションプールの適切なサイズ設定
   - タイムアウト値の最適化
   - メモリ使用量の監視と制御
   - 実装例: implementation_patterns.md の SessionManagerパターン を参照

2. スケーラビリティ
   - 設定の外部化
   - 環境に応じた動的な調整
   - モニタリングと自動調整の仕組み
   - 実装例: implementation_patterns.md の ConfigurationManagerパターン を参照 