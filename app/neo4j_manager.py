"""Neo4jデータベースの管理を行うモジュール。

このモジュールは、Neo4jデータベースとの接続、データの作成・更新・削除・検索を行います。

必要性：
- Neo4jデータベースとの安全な接続
- トランザクション管理
- エラーハンドリング

十分性：
- 接続情報の適切な管理
- セッション・トランザクションの適切な開放
- 詳細なエラーメッセージ
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from neo4j import GraphDatabase, Session
from neo4j.exceptions import Neo4jError

# ロガーの設定
logger = logging.getLogger(__name__)


class Neo4jManager:
    """Neo4jデータベースの管理を行うクラス。

    このクラスは、Neo4jデータベースとの接続、データの作成・更新・削除・検索を行います。

    Attributes:
        _driver: Neo4jドライバーインスタンス
        _uri: データベースのURI
        _username: 接続ユーザー名
        _password: 接続パスワード
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """Neo4jManagerを初期化する。

        Args:
            uri: Neo4jデータベースのURI（オプション）
            username: 接続ユーザー名（オプション）
            password: 接続パスワード（オプション）

        環境変数から接続情報を取得する場合：
            NEO4J_URI: データベースのURI
            neo4j_user: 接続ユーザー名
            neo4j_pswd: 接続パスワード
        """
        self._uri = uri or os.getenv('NEO4J_URI')
        self._username = username or os.getenv('neo4j_user')
        self._password = password or os.getenv('neo4j_pswd')

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

    def _get_session(self) -> Session:
        """Neo4jセッションを取得する。

        Returns:
            Session: Neo4jセッション

        Note:
            セッションはコンテキストマネージャとして使用することを推奨
        """
        return self._driver.session()

    def create_node(
        self,
        labels: List[str],
        properties: Dict[str, Any]
    ) -> Optional[str]:
        """ノードを作成する。

        Args:
            labels: ノードのラベルのリスト
            properties: ノードのプロパティ辞書

        Returns:
            str: 作成されたノードのID、失敗時はNone

        Raises:
            ValueError: 無効な入力パラメータ
        """
        if not labels:
            raise ValueError("At least one label is required")
        if not properties:
            raise ValueError("Properties are required")

        # ラベルとプロパティをエスケープして結合
        labels_str = ':'.join(labels)
        
        try:
            with self._get_session() as session:
                result = session.run(
                    f"""
                    CREATE (n:{labels_str} $props)
                    RETURN elementId(n) as id
                    """,
                    props=properties
                )
                record = result.single()
                return record["id"] if record else None
        except Neo4jError as e:
            logger.error(f"Error creating node: {str(e)}")
            return None

    def find_node(
        self,
        labels: List[str],
        properties: Dict[str, Any]
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
                    RETURN properties(n) as props
                    LIMIT 1
                    """,
                    props=properties
                )
                record = result.single()
                return record["props"] if record else None
        except Neo4jError as e:
            logger.error(f"Error finding node: {str(e)}")
            return None

    def find_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """IDを指定してノードを検索する。

        Args:
            node_id: 検索対象のノードID

        Returns:
            Dict[str, Any]: 見つかったノードのプロパティ辞書、見つからない場合はNone
        """
        try:
            with self._get_session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE elementId(n) = $node_id
                    RETURN properties(n) as props
                    """,
                    node_id=node_id
                )
                record = result.single()
                return record["props"] if record else None
        except Neo4jError as e:
            logger.error(f"Error finding node by ID: {str(e)}")
            return None

    def delete_node(self, node_id: str) -> bool:
        """指定されたIDのノードを削除する。

        Args:
            node_id: 削除対象のノードID

        Returns:
            bool: 削除が成功した場合はTrue、失敗した場合はFalse
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
        properties: Optional[Dict[str, Union[str, int, float, bool, List[Union[str, int, float, bool]]]]] = None
    ) -> bool:
        """2つのノード間にリレーションシップを作成する。

        Args:
            start_node_id: 開始ノードのID
            end_node_id: 終了ノードのID
            rel_type: リレーションシップの種類
            properties: リレーションシップのプロパティ（オプション）

        Returns:
            bool: 作成が成功した場合はTrue、失敗した場合はFalse

        Note:
            propertiesには以下の型のみ指定可能：
            - 文字列
            - 整数
            - 浮動小数点数
            - 真偽値
            - 上記の型のリスト
        """
        if not all([start_node_id, end_node_id, rel_type]):
            return False

        # プロパティが指定されていない場合は空の辞書を使用
        properties = properties or {}

        try:
            with self._get_session() as session:
                # リレーションシップタイプを直接文字列として埋め込む
                query = f"""
                    MATCH (a), (b)
                    WHERE elementId(a) = $start_id AND elementId(b) = $end_id
                    CREATE (a)-[r:{rel_type}]->(b)
                    SET r = $props
                    RETURN type(r)
                """
                result = session.run(
                    query,
                    start_id=start_node_id,
                    end_id=end_node_id,
                    props=properties
                )
                return result.single() is not None
        except Neo4jError as e:
            logger.error(f"Error creating relationship: {str(e)}")
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
            RETURN type(r) as type, properties(r) as properties,
                   elementId(n) as start_node, elementId(m) as end_node
            """
        elif direction == "incoming":
            query = """
            MATCH (m)-[r]->(n)
            WHERE elementId(n) = $node_id
            RETURN type(r) as type, properties(r) as properties,
                   elementId(m) as start_node, elementId(n) as end_node
            """
        else:  # both
            query = """
            MATCH (n)-[r]-(m)
            WHERE elementId(n) = $node_id
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

    def store_entity(
        self,
        label: str,
        entity_id: str,
        properties: Dict[str, Any]
    ) -> Optional[str]:
        """エンティティを保存または更新する。

        Args:
            label: エンティティのラベル
            entity_id: エンティティのID
            properties: エンティティのプロパティ

        Returns:
            str: 作成または更新されたノードのID、失敗時はNone

        Raises:
            ValueError: 無効な入力パラメータ
            Neo4jError: データベース操作エラー
        """
        if not label or not isinstance(label, str):
            raise ValueError("Label must be a non-empty string")
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("Entity ID must be a non-empty string")
        if not properties or not isinstance(properties, dict):
            raise ValueError("Properties must be a non-empty dictionary")

        try:
            with self._get_session() as session:
                # MERGE文を使用して、存在しない場合は作成、存在する場合は更新
                result = session.run(
                    f"""
                    MERGE (n:{label} {{id: $entity_id}})
                    SET n += $properties
                    RETURN elementId(n) as node_id
                    """,
                    entity_id=entity_id,
                    properties=properties
                )
                record = result.single()
                return record["node_id"] if record else None

        except Neo4jError as e:
            logger.error(f"Error storing entity: {str(e)}")
            raise 