"""Neo4jManagerのテストモジュール。"""

import os
import pytest
from unittest.mock import patch, MagicMock
from neo4j.exceptions import Neo4jError
from app.neo4j_manager import Neo4jManager

@pytest.fixture
def mock_env(monkeypatch):
    """環境変数をモックするフィクスチャ。"""
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("neo4j_user", "test_user")
    monkeypatch.setenv("neo4j_pswd", "test_password")

@pytest.fixture
def mock_driver():
    """Neo4jドライバをモックするフィクスチャ。"""
    with patch("neo4j.GraphDatabase.driver") as mock:
        # セッションのモックを作成
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)
        mock_session.run = MagicMock(return_value=None)
        
        # ドライバのセッションメソッドが、モックセッションを返すように設定
        mock_driver = mock.return_value
        mock_driver.session.return_value = mock_session
        
        yield mock_driver

@pytest.fixture
def manager(mock_env, mock_driver):
    """Neo4jManagerのインスタンスを生成するフィクスチャ。"""
    return Neo4jManager()

def test_init_success(mock_env, mock_driver):
    """__init__()が正常に動作することをテスト。"""
    manager = Neo4jManager()
    assert manager.uri == "bolt://localhost:7687"
    assert manager.user == "test_user"
    assert manager.password == "test_password"
    assert manager.driver == mock_driver

def test_init_no_credentials():
    """__init__()が認証情報なしを適切に処理できることをテスト。"""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError) as exc_info:
            Neo4jManager()
        assert "NEO4J_URI" in str(exc_info.value)
        assert "neo4j_user" in str(exc_info.value)
        assert "neo4j_pswd" in str(exc_info.value)

def test_init_partial_credentials(monkeypatch):
    """__init__()が一部の認証情報欠如を適切に処理できることをテスト。"""
    with patch.dict(os.environ, clear=True):
        # URIのみ設定
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
        with pytest.raises(ValueError) as exc_info:
            Neo4jManager()
        assert "neo4j_user" in str(exc_info.value)
        assert "neo4j_pswd" in str(exc_info.value)

        # URIとユーザー名のみ設定
        monkeypatch.setenv("neo4j_user", "test_user")
        with pytest.raises(ValueError) as exc_info:
            Neo4jManager()
        assert "neo4j_pswd" in str(exc_info.value)

def test_init_connection_error(mock_env):
    """__init__()が接続エラーを適切に処理できることをテスト。"""
    with patch("neo4j.GraphDatabase.driver", side_effect=Exception("Connection Error")):
        with pytest.raises(ConnectionError) as exc_info:
            Neo4jManager()
        assert "接続に失敗" in str(exc_info.value)

def test_create_node_success(manager):
    """create_node()が正常に動作することをテスト。"""
    # トランザクションの結果をモック
    mock_record = MagicMock()
    mock_record["node_id"] = "123"
    mock_result = MagicMock()
    mock_result.single.return_value = mock_record

    # セッションのwrite_transactionをモック
    manager.driver.session().__enter__().write_transaction.return_value = "123"

    result = manager.create_node("TestLabel", {"name": "test"})
    assert result == "123"

def test_create_node_invalid_params(manager):
    """create_node()が不正なパラメータを適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        manager.create_node("", {})
    assert "ラベルまたはプロパティ" in str(exc_info.value)

def test_create_node_neo4j_error(manager):
    """create_node()がNeo4jエラーを適切に処理できることをテスト。"""
    manager.driver.session().__enter__().write_transaction.side_effect = Neo4jError("Test Error")
    
    with pytest.raises(Neo4jError):
        manager.create_node("TestLabel", {"name": "test"})

def test_create_relationship_success(manager):
    """create_relationship()が正常に動作することをテスト。"""
    manager.create_relationship("1", "2", "TEST_REL", {"prop": "value"})
    # トランザクションが呼ばれたことを確認
    assert manager.driver.session().__enter__().write_transaction.called

def test_create_relationship_invalid_params(manager):
    """create_relationship()が不正なパラメータを適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        manager.create_relationship("", "2", "", {})
    assert "必須パラメータ" in str(exc_info.value)

def test_create_relationship_neo4j_error(manager):
    """create_relationship()がNeo4jエラーを適切に処理できることをテスト。"""
    manager.driver.session().__enter__().write_transaction.side_effect = Neo4jError("Test Error")
    
    with pytest.raises(Neo4jError):
        manager.create_relationship("1", "2", "TEST_REL", {})

def test_update_node_success(manager):
    """update_node()が正常に動作することをテスト。"""
    manager.update_node("1", {"name": "updated"})
    # トランザクションが呼ばれたことを確認
    assert manager.driver.session().__enter__().write_transaction.called

def test_update_node_invalid_params(manager):
    """update_node()が不正なパラメータを適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        manager.update_node("", {})
    assert "ノードID" in str(exc_info.value)

def test_update_node_neo4j_error(manager):
    """update_node()がNeo4jエラーを適切に処理できることをテスト。"""
    manager.driver.session().__enter__().write_transaction.side_effect = Neo4jError("Test Error")
    
    with pytest.raises(Neo4jError):
        manager.update_node("1", {"name": "updated"})

def test_close(manager):
    """close()が正常に動作することをテスト。"""
    manager.close()
    assert manager.driver.close.called 