"""Neo4jデータベースへの接続と操作を管理するモジュール。"""

import logging
import os
from typing import Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError

logger = logging.getLogger(__name__)

class Neo4jManager:
    """Neo4jデータベースへの接続と操作を管理するクラス。"""

    def __init__(self):
        """
        Neo4jManagerを初期化し、データベースに接続する。

        Raises:
            ValueError: 環境変数が設定されていない場合
            ConnectionError: データベースへの接続に失敗した場合
        """
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("neo4j_user")
        self.password = os.getenv("neo4j_pswd")

        # 認証情報の検証
        missing_vars = []
        if not self.uri:
            missing_vars.append("NEO4J_URI")
        if not self.user:
            missing_vars.append("neo4j_user")
        if not self.password:
            missing_vars.append("neo4j_pswd")
        
        if missing_vars:
            raise ValueError(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")

        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # 接続テスト
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4jデータベースに接続しました。")

        except Exception as e:
            logger.error(f"Neo4jデータベースへの接続に失敗しました: {str(e)}")
            raise ConnectionError(f"Neo4jデータベースへの接続に失敗しました: {str(e)}")

    def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        """
        指定されたラベルとプロパティを持つノードを作成する。

        Args:
            label (str): ノードのラベル
            properties (Dict[str, Any]): ノードのプロパティ

        Returns:
            str: 作成されたノードのID

        Raises:
            ValueError: パラメータが不正な場合
            Neo4jError: クエリ実行に失敗した場合
        """
        if not label or not properties:
            raise ValueError("ラベルまたはプロパティが指定されていません。")

        try:
            with self.driver.session() as session:
                result = session.write_transaction(
                    self._create_node_tx,
                    label,
                    properties
                )
                return result

        except Neo4jError as e:
            logger.error(f"ノードの作成に失敗しました: {str(e)}")
            raise

    def create_relationship(
        self,
        start_id: str,
        end_id: str,
        rel_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """
        2つのノード間にリレーションシップを作成する。

        Args:
            start_id (str): 開始ノードのID
            end_id (str): 終了ノードのID
            rel_type (str): リレーションシップのタイプ
            properties (Dict[str, Any]): リレーションシップのプロパティ

        Raises:
            ValueError: パラメータが不正な場合
            Neo4jError: クエリ実行に失敗した場合
        """
        if not all([start_id, end_id, rel_type]):
            raise ValueError("必須パラメータが指定されていません。")

        try:
            with self.driver.session() as session:
                session.write_transaction(
                    self._create_relationship_tx,
                    start_id,
                    end_id,
                    rel_type,
                    properties or {}
                )

        except Neo4jError as e:
            logger.error(f"リレーションシップの作成に失敗しました: {str(e)}")
            raise

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> None:
        """
        指定されたノードのプロパティを更新する。

        Args:
            node_id (str): 更新対象のノードID
            properties (Dict[str, Any]): 更新するプロパティ

        Raises:
            ValueError: パラメータが不正な場合
            Neo4jError: クエリ実行に失敗した場合
        """
        if not node_id or not properties:
            raise ValueError("ノードIDまたはプロパティが指定されていません。")

        try:
            with self.driver.session() as session:
                session.write_transaction(
                    self._update_node_tx,
                    node_id,
                    properties
                )

        except Neo4jError as e:
            logger.error(f"ノードの更新に失敗しました: {str(e)}")
            raise

    def close(self) -> None:
        """
        データベース接続を閉じる。
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4jデータベース接続を閉じました。")

    @staticmethod
    def _create_node_tx(tx: Session, label: str, properties: Dict[str, Any]) -> str:
        """
        ノード作成のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            label (str): ノードのラベル
            properties (Dict[str, Any]): ノードのプロパティ

        Returns:
            str: 作成されたノードのID
        """
        query = (
            f"CREATE (n:{label} $props) "
            "RETURN id(n) as node_id"
        )
        result = tx.run(query, props=properties)
        record = result.single()
        if record:
            return str(record["node_id"])
        raise Neo4jError("ノードの作成に失敗しました。")

    @staticmethod
    def _create_relationship_tx(
        tx: Session,
        start_id: str,
        end_id: str,
        rel_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """
        リレーションシップ作成のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            start_id (str): 開始ノードのID
            end_id (str): 終了ノードのID
            rel_type (str): リレーションシップのタイプ
            properties (Dict[str, Any]): リレーションシップのプロパティ
        """
        query = (
            "MATCH (a), (b) "
            "WHERE id(a) = $start_id AND id(b) = $end_id "
            f"CREATE (a)-[r:{rel_type} $props]->(b)"
        )
        tx.run(
            query,
            start_id=int(start_id),
            end_id=int(end_id),
            props=properties
        )

    @staticmethod
    def _update_node_tx(tx: Session, node_id: str, properties: Dict[str, Any]) -> None:
        """
        ノード更新のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            node_id (str): 更新対象のノードID
            properties (Dict[str, Any]): 更新するプロパティ
        """
        query = (
            "MATCH (n) "
            "WHERE id(n) = $node_id "
            "SET n += $props"
        )
        tx.run(query, node_id=int(node_id), props=properties) 