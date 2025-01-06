"""テスト用の共通フィクスチャを提供するモジュール。

このモジュールは、テストで使用される共通のフィクスチャを定義します。
主な機能：
1. Neo4jドライバーのモック
2. セッション管理のモック
3. トランザクション管理のモック
"""

from unittest.mock import MagicMock

import pytest
from neo4j.exceptions import AuthError, ServiceUnavailable


class MockTransaction:
    """Neo4jトランザクションをモックするクラス。
    
    このクラスは、Neo4jのトランザクションオブジェクトの振る舞いをシミュレートします。
    主な機能：
    1. クエリの実行
    2. トランザクションのコミット
    3. トランザクションのロールバック
    """

    def __init__(self, session):
        """MockTransactionを初期化する。
        
        Args:
            session: 親となるセッションオブジェクト
        """
        self.session = session
        self.is_closed = False

    def run(self, query, parameters=None):
        """クエリを実行する。
        
        Args:
            query: 実行するクエリ文字列
            parameters: クエリパラメータ（オプション）
            
        Returns:
            クエリ結果のモック
        """
        if self.is_closed:
            raise RuntimeError("Transaction is closed")
        return self.session.run(query, parameters)

    def commit(self):
        """トランザクションをコミットする。"""
        if self.is_closed:
            raise RuntimeError("Transaction is closed")
        self.is_closed = True

    def rollback(self):
        """トランザクションをロールバックする。"""
        if self.is_closed:
            raise RuntimeError("Transaction is closed")
        self.is_closed = True

    def close(self):
        """トランザクションをクローズする。"""
        self.is_closed = True


class MockSession:
    """Neo4jセッションをモックするクラス。
    
    このクラスは、Neo4jのセッションオブジェクトの振る舞いをシミュレートします。
    主な機能：
    1. クエリの実行
    2. トランザクションの開始
    3. セッションのクローズ
    """

    def __init__(self, driver):
        """MockSessionを初期化する。
        
        Args:
            driver: 親となるドライバーオブジェクト
        """
        self.driver = driver
        self.is_closed = False
        self.transaction = None
        self._mock_results = []

    def run(self, query, parameters=None):
        """クエリを実行する。
        
        Args:
            query: 実行するクエリ文字列
            parameters: クエリパラメータ（オプション）
            
        Returns:
            クエリ結果のモック
            
        Raises:
            RuntimeError: セッションがクローズされている場合
        """
        if self.is_closed:
            raise RuntimeError("Session is closed")

        # クエリ結果のモックを作成
        mock_result = MagicMock()
        mock_result.single.return_value = {"node_id": 1, "rel_id": 1}
        mock_result.__iter__.return_value = [{"n": {"name": "test"}}]
        return mock_result

    def begin_transaction(self):
        """新しいトランザクションを開始する。
        
        Returns:
            MockTransactionインスタンス
            
        Raises:
            RuntimeError: セッションがクローズされている場合
        """
        if self.is_closed:
            raise RuntimeError("Session is closed")
        self.transaction = MockTransaction(self)
        return self.transaction

    def close(self):
        """セッションをクローズする。"""
        self.is_closed = True

    def __enter__(self):
        """コンテキストマネージャのエントリーポイント。
        
        Returns:
            self: セッションインスタンス
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャのイグジットポイント。
        
        Args:
            exc_type: 例外の型
            exc_val: 例外値
            exc_tb: トレースバック
        """
        self.close()


@pytest.fixture
def mock_neo4j_driver():
    """Neo4jドライバーのモックを提供する。
    
    このフィクスチャは、Neo4jドライバーの振る舞いをシミュレートするモックオブジェクトを提供します。
    主な機能：
    1. セッションの作成
    2. 接続のクローズ
    3. 認証エラーのシミュレート
    
    Returns:
        MagicMock: Neo4jドライバーのモック
    """
    mock_driver = MagicMock()
    
    def session_factory():
        """セッションファクトリ関数。
        
        Returns:
            MockSession: セッションのモック
        """
        return MockSession(mock_driver)
    
    mock_driver.session = session_factory
    return mock_driver


@pytest.fixture
def mock_auth_error_driver():
    """認証エラーを発生させるNeo4jドライバーのモックを提供する。
    
    このフィクスチャは、認証エラーをシミュレートするためのモックオブジェクトを提供します。
    
    Returns:
        MagicMock: 認証エラーを発生させるドライバーのモック
        
    Raises:
        AuthError: 認証エラーの例外
    """
    mock_driver = MagicMock()
    mock_driver.session.side_effect = AuthError("Invalid credentials")
    return mock_driver


@pytest.fixture
def mock_connection_error_driver():
    """接続エラーを発生させるNeo4jドライバーのモックを提供する。
    
    このフィクスチャは、接続エラーをシミュレートするためのモックオブジェクトを提供します。
    
    Returns:
        MagicMock: 接続エラーを発生させるドライバーのモック
        
    Raises:
        ServiceUnavailable: 接続エラーの例外
    """
    mock_driver = MagicMock()
    mock_driver.session.side_effect = ServiceUnavailable("Cannot connect to Neo4j")
    return mock_driver 