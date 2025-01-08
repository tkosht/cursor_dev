"""Neo4jデータベースとの接続を管理するモジュール。"""

import logging
import os
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Neo4jデータベースの管理を行うクラス。

    このクラスは、Neo4jデータベースとの接続、データの作成・更新・削除・検索を行います。

    Attributes:
        _driver: Neo4jドライバーインスタンス
        _uri: データベースのURI
        _username: 接続ユーザー名
        _password: 接続パスワード
        logger: ロギングインスタンス
    """

    logger = logger  # クラス変数としてloggerを設定

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j"
    ) -> None:
        """Neo4jManagerを初期化する。

        Args:
            uri: Neo4jデータベースのURI（オプション）
            username: 接続ユーザー名（オプション）
            password: 接続パスワード（オプション）
            database: 使用するデータベース名（デフォルト: "neo4j"）

        環境変数から接続情報を取得する場合：
            NEO4J_URI: データベースのURI
            neo4j_user: 接続ユーザー名
            neo4j_pswd: 接続パスワード
        """
        self._uri = uri or os.getenv('NEO4J_URI')
        self._username = username or os.getenv('neo4j_user')
        self._password = password or os.getenv('neo4j_pswd')
        self._database = database

        if not all([self._uri, self._username, self._password]):
            raise ValueError(
                "Database connection information is required. "
                "Please provide either as arguments or environment variables."
            )

        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password)
            )
            # 接続テスト
            with self._driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

    def __del__(self) -> None:
        """デストラクタ。ドライバーを適切にクローズする。"""
        if hasattr(self, '_driver'):
            self._driver.close()

    def _get_session(self):
        """セッションを取得する。

        Returns:
            Session: Neo4jセッションオブジェクト
        """
        return self._driver.session(database=self._database)

    def _execute_transaction(self, work_func):
        """トランザクションを実行する。

        Args:
            work_func (callable): トランザクション内で実行する関数

        Returns:
            Any: work_funcの戻り値
        """
        with self._get_session() as session:
            try:
                return session.execute_write(work_func)
            except Exception as e:
                self.logger.error(f"Transaction error: {str(e)}")
                raise

    def _execute_read_transaction(self, work_func):
        """
        読み取り専用トランザクションを実行する。

        Args:
            work_func: トランザクション内で実行する関数

        Returns:
            Any: work_funcの戻り値
        """
        try:
            with self._get_session() as session:
                return session.execute_read(work_func)
        except Exception as e:
            self.logger.error(f"Transaction error: {str(e)}")
            raise

    def _execute_unit_of_work(self, work_func):
        """
        作業単位を実行する。

        Args:
            work_func: 実行する関数

        Returns:
            Any: work_funcの戻り値
        """
        try:
            with self._get_session() as session:
                with session.begin_transaction() as tx:
                    try:
                        result = work_func(tx)
                        tx.commit()
                        return result
                    except Exception:
                        tx.rollback()
                        raise
        except Exception as e:
            self.logger.error(f"Transaction error: {str(e)}")
            raise

    def create_node(self, labels: List[str], properties: Dict[str, Any]) -> Optional[str]:
        """ノードを作成する。

        Args:
            labels: ノードのラベルリスト
            properties: ノードのプロパティ

        Returns:
            Optional[str]: 作成されたノードのID、失敗時はNone

        Note:
            - トランザクション内で実行され、エラー時は自動的にロールバック
            - プロパティは基本型（str、int、float、bool）のみ許可
        """
        if not labels or not isinstance(labels, list):
            raise ValueError("Labels must be a non-empty list")
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")

        def create_node_tx(tx):
            labels_str = ":".join(labels)
            query = (
                f"CREATE (n:{labels_str} $props) "
                "RETURN elementId(n) as id"
            )
            result = tx.run(query, props=properties)
            record = result.single()
            if not record:
                raise RuntimeError("Failed to create node")
            return record["id"]

        return self._execute_transaction(create_node_tx)

    def find_node(
        self,
        labels: List[str] = None,
        properties: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """指定された条件に一致するノードを検索する。

        Args:
            labels: 検索対象のラベルのリスト
            properties: 検索条件となるプロパティ辞書

        Returns:
            Dict[str, Any]: 見つかったノードのプロパティ辞書、見つからない場合はNone

        Raises:
            ValueError: 無効な入力パラメータ
        """
        if not labels:
            raise ValueError("At least one label is required")
        if not properties:
            raise ValueError("Search properties are required")

        # ラベルを結合
        labels_str = ':'.join(labels)
        
        try:
            with self._get_session() as session:
                result = session.run(
                    f"""
                    MATCH (n:{labels_str})
                    WHERE ALL(key IN keys($props) WHERE n[key] = $props[key])
                    WITH n
                    LIMIT 1
                    RETURN properties(n) as props, elementId(n) as id
                    """,
                    props=properties
                )
                record = result.single()
                if record:
                    props = record["props"]
                    props['id'] = record["id"]
                    return props
                return None
        except Neo4jError as e:
            logger.error(f"Error finding node: {str(e)}")
            return None

    def find_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        IDを指定してノードを検索する。

        Args:
            node_id: 検索対象のノードID

        Returns:
            Dict[str, Any]: 見つかったノードのプロパティ辞書、見つからない場合はNone
        """
        try:
            if not node_id or not isinstance(node_id, (str, int)):
                return None

            with self._get_session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE elementId(n) = $node_id
                    WITH n
                    LIMIT 1
                    RETURN properties(n) as props, elementId(n) as id
                    """,
                    node_id=node_id
                )
                record = result.single()
                if record:
                    props = record["props"]
                    props['id'] = record["id"]
                    return props
                return None
        except Exception as e:
            self.logger.error(f"Error finding node: {str(e)}")
            return None

    def delete_node(self, node_id: str) -> bool:
        """指定されたIDのノードを削除する。

        Args:
            node_id: 削除対象のノードID

        Returns:
            bool: 削除が成功した場合はTrue、失敗したた場合はFalse
        """
        try:
            with self._get_session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE elementId(n) = $node_id
                    DETACH DELETE n
                    """,
                    node_id=node_id
                )
                return result.consume().counters.nodes_deleted > 0
        except Neo4jError as e:
            logger.error(f"Error deleting node: {str(e)}")
            return False

    def create_relationship(
        self,
        start_node_id: str,
        end_node_id: str,
        rel_type: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        2つのノード間にリレーションシップを作成する。

        Args:
            start_node_id: 開始ノードのID
            end_node_id: 終了ノードのID
            rel_type: リレーションシップの種類
            properties: リレーションシップのプロパティ

        Returns:
            bool: 作成成功時True、失敗時False
        """
        def create_relationship_tx(tx):
            try:
                # リレーションシップを作成
                result = tx.run(
                    f"""
                    MATCH (a), (b)
                    WHERE elementId(a) = $start_id AND elementId(b) = $end_id
                    CREATE (a)-[r:{rel_type}]->(b)
                    SET r = $props
                    RETURN r
                    """,
                    start_id=start_node_id,
                    end_id=end_node_id,
                    props=properties
                )
                return result.single() is not None
            except Exception as e:
                self.logger.error(f"Error in relationship transaction: {str(e)}")
                return False

        try:
            if not all([start_node_id, end_node_id, rel_type]):
                return False
            return self._execute_transaction(create_relationship_tx)
        except Exception as e:
            self.logger.error(f"Error creating relationship: {str(e)}")
            return False

    def find_relationships(
        self,
        node_id: str,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """指定されたノードのリレーションシップを検索する。

        Args:
            node_id: 検索対象のノードID
            direction: リレーションシップの方向
                      "outgoing": 出力方向のみ
                      "incoming": 入力方向のみ
                      "both": 両方向（デフォルト）

        Returns:
            List[Dict[str, Any]]: リレーションシップの情報のリスト
                各辞書は以下のキーを含む：
                - type: リレーションシップの種類
                - properties: リレーションシップのプロパティ
                - start_node: 開始ノードのID
                - end_node: 終了ノードのID
        """
        # 方向に応じてCypherクエリを構築
        if direction == "outgoing":
            query = """
            MATCH (n)-[r]->(m)
            WHERE elementId(n) = $node_id
            WITH r, n, m
            RETURN type(r) as type, properties(r) as properties,
                   elementId(n) as start_node, elementId(m) as end_node
            """
        elif direction == "incoming":
            query = """
            MATCH (m)-[r]->(n)
            WHERE elementId(n) = $node_id
            WITH r, n, m
            RETURN type(r) as type, properties(r) as properties,
                   elementId(m) as start_node, elementId(n) as end_node
            """
        else:  # both
            query = """
            MATCH (n)-[r]-(m)
            WHERE elementId(n) = $node_id
            WITH r, n, m
            RETURN type(r) as type, properties(r) as properties,
                   elementId(startNode(r)) as start_node,
                   elementId(endNode(r)) as end_node
            """

        try:
            with self._get_session() as session:
                result = session.run(query, node_id=node_id)
                return [
                    {
                        "type": record["type"],
                        "properties": record["properties"],
                        "start_node": record["start_node"],
                        "end_node": record["end_node"]
                    }
                    for record in result
                ]
        except Neo4jError as e:
            logger.error(f"Error finding relationships: {str(e)}")
            return []

    def _validate_entity(self, entity: Dict[str, Any]) -> None:
        """エンティティの妥当性を検証する。

        Args:
            entity: 検証対象のエンティティ辞書

        Raises:
            ValueError: 無効なエンティティ
        """
        if not isinstance(entity, dict):
            raise ValueError("entity must be a dictionary")
        if not entity:
            raise ValueError("entity is required")
        
        required_fields = ["id", "type", "name", "properties"]
        for field in required_fields:
            if field not in entity:
                raise ValueError(f"entity must have {field} field")

    def _create_relationships(
        self,
        entity_id: str,
        relationships: List[Dict[str, Any]]
    ) -> None:
        """エンティティの関係を作成する。

        Args:
            entity_id: エンティティID
            relationships: 関係情報のリスト
        """
        for rel in relationships:
            if not all(k in rel for k in ["target_id", "type"]):
                continue
            
            # 関係を作成
            rel_props = rel.get("properties", {})
            success = self.create_relationship(
                entity_id,
                rel["target_id"],
                rel["type"],
                rel_props
            )
            if not success:
                logger.warning(
                    f"Failed to create relationship from {entity_id} "
                    f"to {rel['target_id']} of type {rel['type']}"
                )

    def store_entity(
        self,
        entity: Dict[str, Any]
    ) -> bool:
        """エンティティを保存する。

        Args:
            entity: エンティティ情報を含む辞書
                {
                    "id": str,          # エンティティID（必須）
                    "type": str,        # エンティティタイプ（必須）
                    "name": str,        # エンティティ名（必須）
                    "properties": dict, # その他のプロパティ（必須）
                    "relationships": [  # 関係情報（オプション）
                        {
                            "target_id": str,  # 関係先エンティティID
                            "type": str,       # 関係タイプ
                            "properties": dict # 関係のプロパティ
                        }
                    ]
                }

        Returns:
            bool: 保存が成功した場合はTrue、失敗した場場合はFalse

        Raises:
            ValueError: 無効な入力パラメータ
        """
        try:
            # エンティティの妥当性を検証
            self._validate_entity(entity)
            
            # プロパティを準備
            properties = {
                "id": entity["id"],
                "name": entity["name"],
                **entity["properties"]
            }
            
            with self._get_session() as session:
                # エンティティを作成または更新
                query = f"""
                    MERGE (n:Entity:{entity['type']} {{id: $id}})
                    SET n = $props
                    RETURN n
                """
                result = session.run(
                    query,
                    id=entity["id"],
                    props=properties
                )
                if not result.single():
                    return False
                
                # 関係を作成
                if "relationships" in entity and entity["relationships"]:
                    self._create_relationships(
                        entity["id"],
                        entity["relationships"]
                    )
                
                return True
        except Neo4jError as e:
            logger.error(f"Error storing entity: {str(e)}")
            return False

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        ノードを更新する。

        Args:
            node_id: 更新対象のノードID
            properties: 更新するプロパティ

        Returns:
            bool: 更新成功時True、失敗時False
        """
        if not node_id:
            raise ValueError("Node ID must be provided")
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")

        def update_node_tx(tx):
            query = (
                "MATCH (n) "
                "WHERE elementId(n) = $node_id "
                "SET n += $props "
                "RETURN n"
            )
            result = tx.run(query, node_id=node_id, props=properties)
            return result.single() is not None

        return self._execute_transaction(update_node_tx)

    def close(self) -> None:
        """Neo4jドライバーを閉じる。"""
        if hasattr(self, '_driver'):
            self._driver.close() 