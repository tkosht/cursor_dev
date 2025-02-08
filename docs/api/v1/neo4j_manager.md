# Neo4jManager API

## 概要

`Neo4jManager`は、Neo4jデータベースとの相互作用を管理し、トランザクション制御とエラーハンドリングを提供するクラスです。

## 初期化

```python
from app.neo4j_manager import Neo4jManager

manager = Neo4jManager(
    uri="bolt://neo4j:7687",
    username="neo4j",
    password="your_password"
)
```

### パラメータ

- `uri` (str): Neo4jデータベースのURI
  - 必須
  - デフォルト: "bolt://neo4j:7687"
- `username` (str): ユーザー名
  - 必須
  - デフォルト: "neo4j"
- `password` (str): パスワード
  - 必須

### 例外

- `ValidationError`: 接続情報が不正な場合
- `DatabaseError`: データベースへの接続に失敗した場合

## メソッド

### トランザクション管理

#### begin_transaction

新しいトランザクションを開始します。

```python
manager.begin_transaction()
```

##### 例外

- `TransactionError`: 既にアクティブなトランザクションが存在する場合
- `DatabaseError`: トランザクションの開始に失敗した場合

#### commit_transaction

現在のトランザクションをコミットします。

```python
manager.commit_transaction()
```

##### 例外

- `TransactionError`: アクティブなトランザクションが存在しない場合
- `DatabaseError`: コミットに失敗した場合

#### rollback_transaction

現在のトランザクションをロールバックします。

```python
manager.rollback_transaction()
```

##### 例外

- `DatabaseError`: ロールバックに失敗した場合

### ノード操作

#### create_content_node

コンテンツノードを作成します。

```python
node_id = manager.create_content_node({
    "content": "コンテンツ本文",
    "created_at": "2025-01-11T00:00:00"
})
```

##### パラメータ

- `data` (dict): ノードのプロパティ
  - 必須

##### 戻り値

- `str`: 作成されたノードのID

##### 例外

- `ValidationError`: データが不正な形式の場合
- `DatabaseError`: ノードの作成に失敗した場合

#### create_entity_node

エンティティノードを作成します。

```python
node_id = manager.create_entity_node({
    "name": "エンティティ名",
    "type": "ENTITY",
    "created_at": "2025-01-11T00:00:00"
})
```

##### パラメータ

- `data` (dict): ノードのプロパティ
  - 必須

##### 戻り値

- `str`: 作成されたノードのID

##### 例外

- `ValidationError`: データが不正な形式の場合
- `DatabaseError`: ノードの作成に失敗した場合

### リレーションシップ操作

#### create_relationship

リレーションシップを作成します。

```python
rel_id = manager.create_relationship({
    "description": "関係の説明",
    "type": "RELATES_TO",
    "content_id": "content-123"
})
```

##### パラメータ

- `data` (dict): リレーションシップのプロパティ
  - 必須
  - `description`: 関係の説明
  - `type`: 関係の種類
  - `content_id`: コンテンツのID

##### 戻り値

- `str`: 作成されたリレーションシップのID

##### 例外

- `ValidationError`: データが不正な形式の場合
- `DatabaseError`: リレーションシップの作成に失敗した場合

### クエリ実行

#### execute_query

カスタムクエリを実行します。

```python
results = manager.execute_query(
    query="MATCH (n:Entity) RETURN n",
    params={"param1": "value1"}
)
```

##### パラメータ

- `query` (str): 実行するCypherクエリ
  - 必須
- `params` (dict, optional): クエリパラメータ
  - オプション

##### 戻り値

- `List[Dict]`: クエリ結果のリスト

##### 例外

- `ValidationError`: クエリが空の場合
- `DatabaseError`: クエリの実行に失敗した場合

### メトリクス

#### get_metrics

現在のメトリクスを取得します。

```python
metrics = manager.get_metrics()
```

##### 戻り値

```python
{
    "create_node": {
        "total_time": float,  # 合計実行時間
        "call_count": int,    # 呼び出し回数
        "min_time": float,    # 最小実行時間
        "max_time": float     # 最大実行時間
    },
    "create_relationship": {
        "total_time": float,
        "call_count": int,
        "min_time": float,
        "max_time": float
    },
    "execute_query": {
        "total_time": float,
        "call_count": int,
        "min_time": float,
        "max_time": float
    }
}
```

## エラーハンドリング

### リトライ機能

- 一時的なエラーが発生した場合、自動的にリトライを実行
- 最大リトライ回数: 3回
- リトライ間隔: 指数バックオフ（1秒、2秒、4秒）

### コネクション管理

- 接続エラー時は自動的に再接続を試行
- 接続プールを適切に管理し、リソースリークを防止

## 使用例

```python
from app.neo4j_manager import Neo4jManager
from app.exceptions import DatabaseError, ValidationError

# 初期化
manager = Neo4jManager(
    uri="bolt://neo4j:7687",
    username="neo4j",
    password="your_password"
)

try:
    # トランザクション開始
    manager.begin_transaction()
    
    # コンテンツノード作成
    content_id = manager.create_content_node({
        "content": "テスト用コンテンツ",
        "created_at": "2025-01-11T00:00:00"
    })
    
    # エンティティノード作成
    entity_id = manager.create_entity_node({
        "name": "テスト企業",
        "type": "ENTITY",
        "created_at": "2025-01-11T00:00:00"
    })
    
    # リレーションシップ作成
    rel_id = manager.create_relationship({
        "description": "テスト関係",
        "type": "RELATES_TO",
        "content_id": content_id
    })
    
    # トランザクションコミット
    manager.commit_transaction()
    
    # メトリクス確認
    metrics = manager.get_metrics()
    print(f"ノード作成時間: {metrics['create_node']['total_time']}秒")

except ValidationError as e:
    print(f"入力エラー: {str(e)}")
    manager.rollback_transaction()
except DatabaseError as e:
    print(f"データベースエラー: {str(e)}")
    manager.rollback_transaction()
finally:
    manager.close()
``` 