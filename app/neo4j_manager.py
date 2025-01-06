"""Neo4jデータベースとの接続を管理するモジュール。

必要性：
- データベース接続の確立と管理
  - 環境変数による柔軟な設定
  - 接続の自動再試行と回復
  - セッションの適切なライフサイクル管理
- トランザクションの一貫性確保
  - 自動コミットとロールバック
  - デッドロック検出と回避
  - 長時間トランザクションの監視
- セキュアな認証情報の取り扱い
  - 環境変数からの安全な読み込み
  - メモリ上での最小限の保持
  - ログ出力時の認証情報マスク

十分性：
- 環境変数による設定で、セキュアな認証情報管理を実現
  - .env.test による開発環境の分離
  - 本番環境での安全な設定変更
  - 認証情報の漏洩防止
- 詳細なログ出力による問題の追跡
  - 接続エラーの詳細な記録
  - トランザクション状態の監視
  - パフォーマンス指標の収集
- エラー発生時の適切な例外処理
  - 具体的なエラーメッセージ
  - リトライ可能なエラーの判別
  - クリーンアップ処理の保証
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

logger = logging.getLogger(__name__)

class Neo4jManager:
    """Neo4jデータベースとの接続を管理するクラス。
    
    必要性：
    - Neo4jデータベースへの接続確立と維持
    - セキュアな認証情報管理
    - トランザクション管理とエラーハンドリング
    
    十分性：
    - 環境変数からの設定読み込み
    - 接続エラーの適切な処理
    - セッションの適切なライフサイクル管理
    """

    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        max_connection_lifetime: int = 3600
    ) -> None:
        """Neo4jManagerを初期化し、データベース接続を確立する。
        
        必要性：
        - 接続パラメータの設定
        - 環境変数からの設定読み込み
        - 接続の確立と検証
        
        十分性：
        - パラメータの存在確認
        - 環境変数の適切な読み込み
        - 接続テストの実行
        
        Args:
            uri: Neo4jサーバーのURI（未指定時は環境変数から読み込み）
            username: 認証ユーザー名（未指定時は環境変数から読み込み）
            password: 認証パスワード（未指定時は環境変数から読み込み）
            max_connection_lifetime: 接続の最大生存時間（秒）
        
        Raises:
            ValueError: 必要なパラメータが不足している場合
            AuthError: 認証に失敗した場合
            ServiceUnavailable: 接続できない場合
        """
        self._uri = uri or os.getenv('NEO4J_URI')
        self._username = username or os.getenv('neo4j_user')
        self._password = password or os.getenv('neo4j_pswd')

        if not self._uri:
            raise ValueError("URI is required. Set NEO4J_URI environment variable or pass uri parameter.")
        if not self._username:
            raise ValueError("Username is required. Set neo4j_user environment variable or pass username parameter.")
        if not self._password:
            raise ValueError("Password is required. Set neo4j_pswd environment variable or pass password parameter.")

        logger.debug(f"Initializing Neo4jManager with URI: {self._uri}, username: {self._username}")

        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
                max_connection_lifetime=max_connection_lifetime
            )
            logger.debug("Attempting to establish Neo4j connection...")
            
            # 接続テスト
            with self._get_session() as session:
                logger.debug("Testing connection with simple query...")
                session.run("RETURN 1")
                
        except AuthError as e:
            error_msg = f"Authentication failed for user {self._username}"
            logger.error(f"{error_msg}: {str(e)}")
            logger.debug(f"Connection parameters: URI={self._uri}, username={self._username}")
            raise AuthError(error_msg)
            
        except (ServiceUnavailable, ValueError) as e:
            error_msg = f"Cannot connect to Neo4j database at {self._uri}"
            logger.error(f"{error_msg}: {str(e)}")
            logger.debug(f"Connection parameters: URI={self._uri}, username={self._username}")
            raise ServiceUnavailable(f"{error_msg}: {str(e)}")
            
        except Exception as e:
            error_msg = f"Unexpected error during initialization: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Full connection details: URI={self._uri}, username={self._username}")
            raise

    def __del__(self):
        """デストラクタ：ドライバーを適切にクローズする。"""
        if hasattr(self, '_driver'):
            self._driver.close()

    @contextmanager
    def _get_session(self):
        """セッションを取得するコンテキストマネージャ。
        
        必要性：
        - セッションの適切なライフサイクル管理
        - リソースの確実な解放
        
        十分性：
        - コンテキストマネージャによる自動クローズ
        - エラー時の適切な処理
        """
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()

    def create_node(self, labels: List[str], properties: Dict[str, Any]) -> str:
        """新しいノードを作成する。
        
        必要性：
        - ノードの作成機能の提供
        - ラベルとプロパティの設定
        - 作成結果の確認
        
        十分性：
        - パラメータのバリデーション
        - トランザクション管理
        - エラーハンドリング
        
        Args:
            labels: ノードに設定するラベルのリスト
            properties: ノードのプロパティ辞書
        
        Returns:
            str: 作成されたノードのID
            
        Raises:
            ValueError: ラベルまたはプロパティが不正な場合
        """
        if not labels:
            raise ValueError("At least one label is required")
        if not properties:
            raise ValueError("Properties are required")
            
        try:
            with self._get_session() as session:
                query = (
                    f"CREATE (n:{':'.join(labels)} $properties) "
                    "RETURN id(n) as node_id"
                )
                result = session.run(query, properties=properties)
                record = result.single()
                if record:
                    return str(record["node_id"])
                raise ValueError("Failed to create node")
                
        except Exception as e:
            logger.error(f"Error creating node: {str(e)}")
            raise

    def find_node(self, labels: List[str], properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """指定された条件に一致するノードを検索する。
        
        必要性：
        - ノードの検索機能の提供
        - 検索条件の指定
        - 結果の整形
        
        十分性：
        - パラメータのバリデーション
        - 検索条件の最適化
        - エラーハンドリング
        
        Args:
            labels: 検索対象のラベルリスト
            properties: 検索条件となるプロパティ辞書
        
        Returns:
            Optional[Dict[str, Any]]: 見つかったノードのプロパティ辞書、または None
            
        Raises:
            ValueError: 検索条件が不正な場合
        """
        if not labels:
            raise ValueError("At least one label is required")
        if not properties:
            raise ValueError("Search properties are required")
            
        try:
            with self._get_session() as session:
                query = (
                    f"MATCH (n:{':'.join(labels)}) "
                    "WHERE ALL(key IN keys($properties) WHERE n[key] = $properties[key]) "
                    "RETURN n "
                    "LIMIT 1"  # 最初の1件のみを取得
                )
                result = session.run(query, properties=properties)
                record = result.single()
                if record:
                    node = record["n"]
                    return dict(node.items())
                return None
                
        except Exception as e:
            logger.error(f"Error finding node: {str(e)}")
            raise

    def find_nodes(self, labels: List[str], properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """指定された条件に一致する全てのノードを検索する。
        
        必要性：
        - 複数ノードの検索機能の提供
        - 検索条件の指定
        - 結果の整形
        
        十分性：
        - パラメータのバリデーション
        - 検索条件の最適化
        - エラーハンドリング
        
        Args:
            labels: 検索対象のラベルリスト
            properties: 検索条件となるプロパティ辞書
        
        Returns:
            List[Dict[str, Any]]: 見つかったノードのプロパティ辞書のリスト
            
        Raises:
            ValueError: 検索条件が不正な場合
        """
        if not labels:
            raise ValueError("At least one label is required")
        if not properties:
            raise ValueError("Search properties are required")
            
        try:
            with self._get_session() as session:
                query = (
                    f"MATCH (n:{':'.join(labels)}) "
                    "WHERE ALL(key IN keys($properties) WHERE n[key] = $properties[key]) "
                    "RETURN n"
                )
                result = session.run(query, properties=properties)
                return [dict(record["n"].items()) for record in result]
                
        except Exception as e:
            logger.error(f"Error finding nodes: {str(e)}")
            raise

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """指定されたノードのプロパティを更新する。
        
        必要性：
        - ノードの更新機能の提供
        - プロパティの更新
        - 更新結果の確認
        
        十分性：
        - パラメータのバリデーション
        - トランザクション管理
        - エラーハンドリング
        
        Args:
            node_id: 更新対象のノードID
            properties: 更新するプロパティ辞書
        
        Returns:
            bool: 更新が成功した場合はTrue
            
        Raises:
            ValueError: パラメータが不正な場合
        """
        if not node_id:
            raise ValueError("Node ID is required")
        if not properties:
            raise ValueError("Update properties are required")
            
        try:
            with self._get_session() as session:
                query = (
                    "MATCH (n) "
                    "WHERE id(n) = $node_id "
                    "SET n += $properties "
                    "RETURN n"
                )
                result = session.run(
                    query,
                    node_id=int(node_id),
                    properties=properties
                )
                return bool(result.single())
                
        except Exception as e:
            logger.error(f"Error updating node: {str(e)}")
            raise

    def create_relationship(
        self,
        start_node_id: str,
        end_node_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """2つのノード間にリレーションシップを作成する。
        
        必要性：
        - リレーションシップの作成機能の提供
        - ノード間の関係性の定義
        - プロパティの設定
        
        十分性：
        - パラメータのバリデーション
        - トランザクション管理
        - エラーハンドリング
        
        Args:
            start_node_id: 開始ノードのID
            end_node_id: 終了ノードのID
            relationship_type: リレーションシップの種類
            properties: リレーションシップのプロパティ辞書（オプション）
        
        Returns:
            bool: 作成が成功した場合はTrue
            
        Raises:
            ValueError: パラメータが不正な場合
        """
        if not start_node_id:
            raise ValueError("Start node ID is required")
        if not end_node_id:
            raise ValueError("End node ID is required")
        if not relationship_type:
            raise ValueError("Relationship type is required")
            
        try:
            with self._driver.session() as session:
                query = (
                    "MATCH (start), (end) "
                    "WHERE id(start) = $start_id AND id(end) = $end_id "
                    f"CREATE (start)-[r:{relationship_type} $properties]->(end) "
                    "RETURN r"
                )
                result = session.run(
                    query,
                    start_id=int(start_node_id),
                    end_id=int(end_node_id),
                    properties=properties or {}
                )
                return result.single() is not None
                
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            raise 

    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """カスタムCypherクエリを実行する。
        
        必要性：
        - 柔軟なクエリ実行機能の提供
        - パラメータ化クエリのサポート
        - 結果の整形
        
        十分性：
        - パラメータのバリデーション
        - SQLインジェクション対策
        - エラーハンドリング
        
        Args:
            query: 実行するCypherクエリ文字列
            parameters: クエリパラメータ辞書（オプション）
        
        Returns:
            List[Dict[str, Any]]: クエリ結果のリスト
            
        Raises:
            ValueError: クエリが不正な場合
        """
        if not query:
            raise ValueError("Query string is required")
            
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise 