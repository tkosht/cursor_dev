# API ドキュメント v1.1.1

このドキュメントは、Adoptive Market Crawlerの主要なAPIについて説明します。

## 概要

Adoptive Market Crawlerは以下の主要なAPIクラスを提供します：

1. `GeminiAnalyzer`: Gemini APIを使用したコンテンツ分析
2. `Neo4jManager`: Neo4jデータベース管理
3. `MarketAnalyzer`: 市場分析と知識管理

## API一覧

### GeminiAnalyzer

コンテンツを解析し、エンティティとリレーションシップを抽出するAPIを提供します。

- [GeminiAnalyzer API詳細](./gemini_analyzer.md)

### Neo4jManager

Neo4jデータベースとの相互作用を管理するAPIを提供します。

- [Neo4jManager API詳細](./neo4j_manager.md)

### MarketAnalyzer

市場分析と知識管理のための高レベルAPIを提供します。

- [MarketAnalyzer API詳細](./market_analyzer.md)

## エラーハンドリング

すべてのAPIは以下の例外クラスを使用します：

- `ValidationError`: 入力値が不正な場合
- `GeminiAPIError`: Gemini API呼び出しに失敗した場合
- `DatabaseError`: データベース操作に失敗した場合
- `ServiceUnavailable`: サービスが一時的に利用できない場合
- `TransactionError`: トランザクション操作に失敗した場合

## メトリクス

各APIクラスは`get_metrics()`メソッドを提供し、以下の情報を取得できます：

- API呼び出しの成功率と応答時間
- エラー発生率とリカバリー成功率
- リソース使用状況
- パフォーマンス指標

## バージョニング

APIのバージョニングは[セマンティックバージョニング](https://semver.org/)に従います：

- MAJOR: 後方互換性のない変更
- MINOR: 後方互換性のある機能追加
- PATCH: 後方互換性のあるバグ修正 