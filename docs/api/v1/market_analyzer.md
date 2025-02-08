# MarketAnalyzer API

## 概要

`MarketAnalyzer`は、市場分析と知識管理のための高レベルAPIを提供するクラスです。`GeminiAnalyzer`と`Neo4jManager`を組み合わせて、コンテンツの解析から知識の保存までを一貫して管理します。

## 初期化

```python
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager
from app.gemini_analyzer import GeminiAnalyzer

# 依存オブジェクトの初期化
neo4j_manager = Neo4jManager(
    uri="bolt://neo4j:7687",
    username="neo4j",
    password="your_password"
)
gemini_analyzer = GeminiAnalyzer(api_key="your_gemini_api_key")

# MarketAnalyzerの初期化
analyzer = MarketAnalyzer(
    neo4j_manager=neo4j_manager,
    gemini_analyzer=gemini_analyzer
)
```

### パラメータ

- `neo4j_manager` (Neo4jManager): Neo4jデータベース管理オブジェクト
  - 必須
- `gemini_analyzer` (GeminiAnalyzer): Gemini API分析オブジェクト
  - 必須

### 例外

- `ValidationError`: 引数が不正な場合

## メソッド

### analyze_content

コンテンツを分析し、エンティティとリレーションシップを抽出して保存します。

```python
result = analyzer.analyze_content(content="分析対象のテキスト")
```

#### パラメータ

- `content` (str): 分析対象のコンテンツ
  - 必須

#### 戻り値

```python
{
    "content_id": "content-123",
    "entities": ["エンティティ1", "エンティティ2", ...],
    "relationships": ["リレーションシップの説明1", "リレーションシップの説明2", ...]
}
```

#### 例外

- `ValidationError`: コンテンツが不正な場合
- `DatabaseError`: データベース操作に失敗した場合

### get_market_trends

指定された期間の市場トレンドを取得します。

```python
trends = analyzer.get_market_trends(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

#### パラメータ

- `start_date` (Optional[datetime]): 開始日時
  - オプション
- `end_date` (Optional[datetime]): 終了日時
  - オプション

#### 戻り値

```python
[
    {
        "title": "トレンド1",
        "url": "http://example.com/1",
        "published_at": "2025-01-01T00:00:00",
        "market_impact": 0.8
    },
    ...
]
```

#### 例外

- `MarketAnalysisError`: トレンドの取得に失敗した場合

### get_entity_relationships

指定されたエンティティの関係を取得します。

```python
relationships = analyzer.get_entity_relationships(entity_name="企業A")
```

#### パラメータ

- `entity_name` (str): エンティティ名
  - 必須

#### 戻り値

```python
[
    {
        "source": "企業A",
        "target": "企業B",
        "type": "COMPETES_WITH",
        "strength": 0.7
    },
    ...
]
```

#### 例外

- `MarketAnalysisError`: 関係の取得に失敗した場合

### get_metrics

現在のメトリクスを取得します。

```python
metrics = analyzer.get_metrics()
```

#### 戻り値

```python
{
    "entity_count": int,          # エンティティ総数
    "relationship_count": int,    # リレーションシップ総数
    "timestamp": str             # タイムスタンプ
}
```

## エラーハンドリング

### ロールバック機能

- データベース操作に失敗した場合、自動的にロールバック
- 作成されたノードとリレーションシップを追跡し、必要に応じて削除

### メトリクス記録

- 各操作の成功/失敗を記録
- パフォーマンス指標を収集
- エラー発生時の状況を詳細に記録

## 使用例

```python
from datetime import datetime
from app.market_analyzer import MarketAnalyzer
from app.neo4j_manager import Neo4jManager
from app.gemini_analyzer import GeminiAnalyzer
from app.exceptions import ValidationError, DatabaseError, MarketAnalysisError

# 初期化
neo4j_manager = Neo4jManager(
    uri="bolt://neo4j:7687",
    username="neo4j",
    password="your_password"
)
gemini_analyzer = GeminiAnalyzer(api_key="your_gemini_api_key")
analyzer = MarketAnalyzer(
    neo4j_manager=neo4j_manager,
    gemini_analyzer=gemini_analyzer
)

try:
    # コンテンツ分析
    content = """
    株式会社Aは新製品Xを発表し、市場シェア20%を獲得しました。
    競合他社のBは対抗製品Yの開発を発表しています。
    """
    result = analyzer.analyze_content(content)
    print(f"分析結果: {result}")
    
    # 市場トレンドの取得
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 31)
    trends = analyzer.get_market_trends(start_date, end_date)
    print(f"市場トレンド: {trends}")
    
    # エンティティ関係の取得
    relationships = analyzer.get_entity_relationships("企業A")
    print(f"エンティティ関係: {relationships}")
    
    # メトリクスの確認
    metrics = analyzer.get_metrics()
    print(f"メトリクス: {metrics}")

except ValidationError as e:
    print(f"入力エラー: {str(e)}")
except DatabaseError as e:
    print(f"データベースエラー: {str(e)}")
except MarketAnalysisError as e:
    print(f"市場分析エラー: {str(e)}")
``` 