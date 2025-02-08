"""Neo4jデータベースを管理するモジュール。"""

import logging
import time
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Session
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from .exceptions import DatabaseError, TransactionError, ValidationError
from .monitoring import PerformanceMonitor
from .utils.error_handlers import retry_on_error, validate_input

logger = logging.getLogger(__name__)


def validate_node_data(data: dict) -> bool:
    """
    ノードデータの形式を検証する。

    Args:
        data (dict): 検証対象のデータ

    Returns:
        bool: 検証結果
    """
    return isinstance(data, dict) and len(data) > 0


def validate_relationship_data(data: dict) -> bool:
    """
    リレーションシップデータの形式を検証する。

    Args:
        data (dict): 検証対象のデータ

    Returns:
        bool: 検証結果
    """
    required_fields = ['description', 'type', 'content_id']
    return (
        isinstance(data, dict) and
        all(k in data for k in required_fields)
    )


class Neo4jManager:
    """Neo4jデータベースを管理するクラス。"""

    MAX_RETRY_COUNT = 3
    RETRY_DELAY = 1.0

    def __init__(self, uri: str, username: str, password: str):
        """
        Neo4jManagerを初期化する。

        Args:
            uri (str): Neo4jデータベースのURI
            username (str): ユーザ名
            password (str): パスワード

        Raises:
            ValidationError: 接続情報が不正な場合
            DatabaseError: データベースへの接続に失敗した場合
        """
        if not uri or not username or not password:
            logger.error("データベース接続情報が不正です: URI, username, passwordのいずれかが未設定")
            raise ValidationError("データベース接続情報が不正です")

        try:
            logger.info(f"Neo4jデータベースに接続を試みます: {uri}")
            self._driver = GraphDatabase.driver(uri, auth=(username, password))
            self._verify_connection()
            self._monitor = PerformanceMonitor()
            self._transaction = None
            self._active_session = None
            logger.info("Neo4jデータベースへの接続が成功しました")
        except Exception as e:
            error_msg = f"データベース接続エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseError(error_msg)

    def begin_transaction(self) -> None:
        """
        新しいトランザクションを開始する。

        Raises:
            DatabaseError: トランザクションの開始に失敗した場合
            TransactionError: 既にアクティブなトランザクションが存在する場合
        """
        try:
            if self._transaction:
                raise TransactionError("既にアクティブなトランザクションが存在します")
            
            self._active_session = self._driver.session()
            self._transaction = self._active_session.begin_transaction()
            logger.info("新しいトランザクションを開始しました")
        except Exception as e:
            error_msg = f"トランザクションの開始に失敗しました: {str(e)}"
            logger.error(error_msg)
            self._cleanup_transaction()
            raise DatabaseError(error_msg)

    def commit_transaction(self) -> None:
        """
        現在のトランザクションをコミットする。

        Raises:
            DatabaseError: コミットに失敗した場合
            TransactionError: アクティブなトランザクションが存在しない場合
        """
        if not self._transaction:
            raise TransactionError("アクティブなトランザクションが存在しません")

        try:
            self._transaction.commit()
            logger.info("トランザクションをコミットしました")
        except Exception as e:
            error_msg = f"トランザクションのコミットに失敗しました: {str(e)}"
            logger.error(error_msg)
            self._cleanup_transaction()
            raise DatabaseError(error_msg)
        finally:
            self._cleanup_transaction()

    def rollback_transaction(self) -> None:
        """
        現在のトランザクションをロールバックする。

        Raises:
            DatabaseError: ロールバックに失敗した場合
        """
        if not self._transaction:
            logger.warning("ロールバック対象のトランザクションが存在しません")
            return

        try:
            self._transaction.rollback()
            logger.info("トランザクションをロールバックしました")
        except Exception as e:
            error_msg = f"トランザクションのロールバックに失敗しました: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)
        finally:
            self._cleanup_transaction()

    def _cleanup_transaction(self) -> None:
        """トランザクションとセッションのクリーンアップを行う。"""
        try:
            if self._transaction:
                self._transaction = None
            if self._active_session:
                self._active_session.close()
                self._active_session = None
        except Exception as e:
            logger.error(f"トランザクションのクリーンアップに失敗しました: {str(e)}")

    def close(self) -> None:
        """
        データベース接続を閉じる。

        Raises:
            DatabaseError: 接続のクローズに失敗した場合
        """
        try:
            if self._driver:
                self._driver.close()
        except Exception as e:
            logger.error(f"データベース接続のクローズに失敗しました: {str(e)}")
            raise DatabaseError(f"データベース接続のクローズに失敗しました: {str(e)}")

    def _verify_connection(self) -> None:
        """
        データベース接続を検証する。

        Raises:
            DatabaseError: 接続検証に失敗した場合
        """
        retry_count = 0
        last_error = None

        while retry_count < self.MAX_RETRY_COUNT:
            try:
                with self._driver.session() as session:
                    # 基本的な接続テスト
                    result = session.run("RETURN 1 as num").single()
                    if result and result["num"] == 1:
                        logger.info("データベース接続の検証に成功しました")
                        return
                    else:
                        raise DatabaseError("接続テストの結果が不正です")

            except (ServiceUnavailable, SessionExpired) as e:
                retry_count += 1
                last_error = e
                if retry_count < self.MAX_RETRY_COUNT:
                    logger.warning(
                        f"接続検証リトライ {retry_count}/{self.MAX_RETRY_COUNT} "
                        f"エラー: {str(e)}"
                    )
                    time.sleep(self.RETRY_DELAY * (2 ** retry_count))
                    continue
            except Exception as e:
                error_msg = f"データベース接続の検証に失敗しました: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise DatabaseError(error_msg)

        error_msg = f"{self.MAX_RETRY_COUNT}回の接続検証に失敗しました: {str(last_error)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg)

    @retry_on_error(max_retries=3, retry_delay=1.0)
    @validate_input(validate_node_data)
    def create_content_node(self, data: dict) -> str:
        """
        コンテンツノードを作成する。

        Args:
            data (dict): ノードのプロパティ

        Returns:
            str: 作成されたノードのID

        Raises:
            ValidationError: データが不正な形式の場合
            DatabaseError: ノードの作成に失敗した場合
        """
        try:
            self._monitor.start_measurement('create_node')
            with self._driver.session() as session:
                result = session.write_transaction(self._create_content_node_tx, data)
                self._monitor.end_measurement('create_node')
                return result
        except Exception as e:
            self._monitor.end_measurement('create_node')
            logger.error(f"コンテンツノードの作成に失敗しました: {str(e)}")
            raise DatabaseError(f"コンテンツノードの作成に失敗しました: {str(e)}")

    def _create_content_node_tx(self, tx: Session, data: dict) -> str:
        """
        コンテンツノード作成のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            data (dict): ノードのプロパティ

        Returns:
            str: 作成されたノードのID

        Raises:
            TransactionError: トランザクションの実行に失敗した場合
        """
        try:
            query = """
            CREATE (c:Content)
            SET c += $data, c.created_at = datetime()
            RETURN id(c) as node_id
            """
            result = tx.run(query, data=data)
            record = result.single()
            if not record:
                raise TransactionError("ノードの作成に失敗しました")
            return str(record["node_id"])
        except Exception as e:
            logger.error(f"トランザクションの実行に失敗しました: {str(e)}")
            raise TransactionError(f"トランザクションの実行に失敗しました: {str(e)}")

    @retry_on_error(max_retries=3, retry_delay=1.0)
    @validate_input(validate_node_data)
    def create_entity_node(self, data: dict) -> str:
        """
        エンティティノードを作成する。

        Args:
            data (dict): ノードのプロパティ

        Returns:
            str: 作成されたノードのID

        Raises:
            ValidationError: データが不正な形式の場合
            DatabaseError: ノードの作成に失敗した場合
        """
        try:
            self._monitor.start_measurement('create_node')
            with self._driver.session() as session:
                result = session.write_transaction(self._create_entity_node_tx, data)
                self._monitor.end_measurement('create_node')
                return result
        except Exception as e:
            self._monitor.end_measurement('create_node')
            logger.error(f"エンティティノードの作成に失敗しました: {str(e)}")
            raise DatabaseError(f"エンティティノードの作成に失敗しました: {str(e)}")

    def _create_entity_node_tx(self, tx: Session, data: dict) -> str:
        """
        エンティティノード作成のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            data (dict): ノードのプロパティ

        Returns:
            str: 作成されたノードのID

        Raises:
            TransactionError: トランザクションの実行に失敗した場合
        """
        try:
            query = """
            CREATE (e:Entity)
            SET e += $data, e.created_at = datetime()
            RETURN id(e) as node_id
            """
            result = tx.run(query, data=data)
            record = result.single()
            if not record:
                raise TransactionError("ノードの作成に失敗しました")
            return str(record["node_id"])
        except Exception as e:
            logger.error(f"トランザクションの実行に失敗しました: {str(e)}")
            raise TransactionError(f"トランザクションの実行に失敗しました: {str(e)}")

    @retry_on_error(max_retries=3, retry_delay=1.0)
    @validate_input(validate_relationship_data)
    def create_relationship(self, data: dict) -> str:
        """
        リレーションシップを作成する。

        Args:
            data (dict): リレーションシップのプロパティ
                - description (str): 関係の説明
                - type (str): 関係の種類
                - content_id (str): コンテンツのID

        Returns:
            str: 作成されたリレーションシップのID

        Raises:
            ValidationError: データが不正な形式の場合
            DatabaseError: リレーションシップの作成に失敗した場合
        """
        try:
            self._monitor.start_measurement('create_relationship')
            with self._driver.session() as session:
                result = session.write_transaction(self._create_relationship_tx, data)
                self._monitor.end_measurement('create_relationship')
                return result
        except Exception as e:
            self._monitor.end_measurement('create_relationship')
            logger.error(f"リレーションシップの作成に失敗しました: {str(e)}")
            raise DatabaseError(f"リレーションシップの作成に失敗しました: {str(e)}")

    def _create_relationship_tx(self, tx: Session, data: dict) -> str:
        """
        リレーションシップ作成のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            data (dict): リレーションシップのプロパティ

        Returns:
            str: 作成されたリレーションシップのID

        Raises:
            DatabaseError: リレーションシップの作成に失敗した場合
        """
        try:
            query = (
                "MATCH (c:Content {id: $content_id}) "
                "CREATE (c)-[r:RELATES {description: $description, type: $type}]->(c) "
                "RETURN id(r) as relationship_id"
            )
            result = tx.run(query, data).single()
            if result:
                return str(result["relationship_id"])
            else:
                raise DatabaseError("リレーションシップの作成に失敗しました")
        except Exception as e:
            logger.error(f"リレーションシップの作成に失敗しました: {str(e)}")
            raise DatabaseError(f"リレーションシップの作成に失敗しました: {str(e)}")

    def execute_query(self, query: str, params: Optional[dict] = None) -> List[Dict]:
        """
        カスタムクエリを実行する。

        Args:
            query (str): 実行するCypherクエリ
            params (dict, optional): クエリパラメータ

        Returns:
            List[Dict]: クエリ結果のリスト

        Raises:
            ValidationError: クエリが空の場合
            DatabaseError: クエリの実行に失敗した場合
        """
        if not query:
            raise ValidationError("クエリが指定されていません")

        try:
            self._monitor.start_measurement('execute_query')
            with self._driver.session() as session:
                result = session.run(query, params or {})
                records = [dict(record) for record in result]
                self._monitor.end_measurement('execute_query')
                return records
        except Exception as e:
            self._monitor.end_measurement('execute_query')
            logger.error(f"クエリの実行に失敗しました: {str(e)}")
            raise DatabaseError(f"クエリの実行に失敗しました: {str(e)}")

    def get_metrics(self) -> dict:
        """
        現在のメトリクスを取得する。

        Returns:
            dict: 収集されたメトリクス
        """
        return self._monitor.get_metrics()

    def __enter__(self) -> 'Neo4jManager':
        """
        コンテキストマネージャのエントリーポイント。

        Returns:
            Neo4jManager: 自身のインスタンス
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        コンテキストマネージャの終了処理。

        Args:
            exc_type: 例外の型
            exc_val: 例外の値
            exc_tb: トレースバック情報
        """
        self.close() 

    @retry_on_error(max_retries=3, retry_delay=1.0)
    def save_analysis_result(self, result: Dict[str, Any]) -> None:
        """
        解析結果をNeo4jに保存する。

        Args:
            result (Dict[str, Any]): 解析結果

        Raises:
            ValidationError: データが不正な形式の場合
            DatabaseError: 保存に失敗した場合
        """
        if not isinstance(result, dict):
            raise ValidationError("解析結果は辞書形式である必要があります")

        try:
            self._monitor.start_measurement('save_analysis')
            with self._driver.session() as session:
                session.execute_write(self._save_analysis_result_tx, result)
                self._monitor.end_measurement('save_analysis')
        except Exception as e:
            self._monitor.end_measurement('save_analysis')
            logger.error(f"解析結果の保存に失敗しました: {str(e)}")
            raise DatabaseError(f"解析結果の保存に失敗しました: {str(e)}")

    def _save_analysis_result_tx(self, tx: Session, result: Dict[str, Any]) -> None:
        """
        解析結果保存のトランザクション。

        Args:
            tx (Session): トランザクションセッション
            result (Dict[str, Any]): 解析結果

        Raises:
            DatabaseError: トランザクションの実行に失敗した場合
        """
        try:
            # 解析結果ノードを作成
            query = """
            CREATE (a:Analysis)
            SET a += $result,
                a.created_at = datetime()
            """
            tx.run(query, result=result)
        except Exception as e:
            logger.error(f"解析結果の保存トランザクションに失敗しました: {str(e)}")
            raise DatabaseError(f"解析結果の保存トランザクションに失敗しました: {str(e)}")

    @retry_on_error(max_retries=3, retry_delay=1.0)
    def get_latest_analysis(self) -> Dict[str, Any]:
        """
        最新の解析結果を取得する。

        Returns:
            Dict[str, Any]: 最新の解析結果

        Raises:
            DatabaseError: 取得に失敗した場合
        """
        try:
            self._monitor.start_measurement('get_latest_analysis')
            with self._driver.session() as session:
                result = session.execute_read(self._get_latest_analysis_tx)
                self._monitor.end_measurement('get_latest_analysis')
                return result
        except Exception as e:
            self._monitor.end_measurement('get_latest_analysis')
            logger.error(f"最新の解析結果の取得に失敗しました: {str(e)}")
            raise DatabaseError(f"最新の解析結果の取得に失敗しました: {str(e)}")

    def _get_latest_analysis_tx(self, tx: Session) -> Dict[str, Any]:
        """
        最新の解析結果取得のトランザクション。

        Args:
            tx (Session): トランザクションセッション

        Returns:
            Dict[str, Any]: 最新の解析結果

        Raises:
            DatabaseError: トランザクションの実行に失敗した場合
        """
        try:
            query = """
            MATCH (a:Analysis)
            RETURN a
            ORDER BY a.created_at DESC
            LIMIT 1
            """
            result = tx.run(query).single()
            if result:
                return dict(result["a"])
            else:
                return {}
        except Exception as e:
            logger.error(f"最新の解析結果の取得トランザクションに失敗しました: {str(e)}")
            raise DatabaseError(f"最新の解析結果の取得トランザクションに失敗しました: {str(e)}") 