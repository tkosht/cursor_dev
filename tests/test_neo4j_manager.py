"""Neo4jManagerのテニットテストモジュール。

このモジュールは、Neo4jManagerクラスの各メソッドの動作を検証します。

必要性：
- 各メソッドの正常系・異常系の動作確認
- エラーハンドリングの検証
- 環境変数対応の確認

十分性：
- 実際のNeo4jインスタンスを使用した結合テスト
- 詳細なアサーション
- エラーメッセージの検証
"""

import os
import pytest
from dotenv import load_dotenv
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.neo4j_manager import Neo4jManager

# テスト用の環境変数を読み込む
load_dotenv('.env.test')

def test_init_with_env_vars():
    """環境変数を使用した初期化の成功ケースをテストする。
    
    必要性：
    - 環境変数からの接続情報取得を確認
    - 認証情報の正しい処理を検証
    
    十分性：
    - 環境変数の正しい読み込み
    - 実際のNeo4jインスタンスへの接続確認
    """
    manager = Neo4jManager()
    assert manager._uri == os.getenv('NEO4J_URI')
    assert manager._username == os.getenv('neo4j_user')


def test_init_success():
    """直接パラメータを使用した初期化の成功ケースをテストする。
    
    必要性：
    - 正常な接続確立を確認
    - 認証情報の正しい処理を検証
    
    十分性：
    - 必須パラメータの検証
    - 実際のNeo4jインスタンスへの接続確認
    """
    manager = Neo4jManager(
        uri=os.getenv('NEO4J_URI'),
        username=os.getenv('neo4j_user'),
        password=os.getenv('neo4j_pswd')
    )
    assert manager._uri == os.getenv('NEO4J_URI')
    assert manager._username == os.getenv('neo4j_user')


def test_init_missing_env_vars(monkeypatch):
    """環境変数が不足している場合のエラーケースをテストする。
    
    必要性：
    - 環境変数不足時の適切なエラー処理を確認
    - エラーメッセージの正確性を検証
    
    十分性：
    - 各環境変数不足時のケース
    - エラーメッセージの内容確認
    """
    # 環境変数をクリア
    monkeypatch.delenv('NEO4J_URI', raising=False)
    monkeypatch.delenv('neo4j_user', raising=False)
    monkeypatch.delenv('neo4j_pswd', raising=False)

    with pytest.raises(ValueError) as exc_info:
        Neo4jManager()
    assert "URI is required" in str(exc_info.value)


def test_init_auth_error():
    """認証エラーケースをテストする。
    
    必要性：
    - 認証失敗時の適切なエラー処理を確認
    - エラーメッセージの正確性を検証
    
    十分性：
    - 例外の型の検証
    - エラーメッセージの内容確認
    """
    with pytest.raises(AuthError) as exc_info:
        Neo4jManager(
            uri=os.getenv('NEO4J_URI'),
            username="invalid",
            password="invalid"
        )
    assert "Authentication failed" in str(exc_info.value)


def test_init_connection_error():
    """接続エラーケースをテストする。
    
    必要性：
    - 接続失敗時の適切なエラー処理を確認
    - エラーメッセージの正確性を検証
    
    十分性：
    - 例外の型の検証
    - エラーメッセージの内容確認
    """
    with pytest.raises(ServiceUnavailable) as exc_info:
        Neo4jManager(
            uri="bolt://invalid:7687",
            username=os.getenv('neo4j_user'),
            password=os.getenv('neo4j_pswd')
        )
    assert "Cannot connect to Neo4j" in str(exc_info.value)


def test_create_node_success():
    """ノード作成の成功ケースをテストする。
    
    必要性：
    - ノードの正常な作成を確認
    - 返却値の正確性を検証
    
    十分性：
    - ラベルとプロパティの正しい設定
    - 作成されたノードIDの検証
    """
    manager = Neo4jManager()
    
    node_id = manager.create_node(
        labels=["Person"],
        properties={"name": "Test Person"}
    )
    
    assert node_id is not None
    assert isinstance(node_id, str)


def test_create_node_validation_error():
    """ノード作成の入力検証エラーケースをテストする。
    
    必要性：
    - 無効な入力パラメータの検出を確認
    - 適切なエラーメッセージの生成を検証
    
    十分性：
    - ラベル未指定のケース
    - プロパティ未指定のケース
    """
    manager = Neo4jManager()
    
    with pytest.raises(ValueError) as exc_info:
        manager.create_node(labels=[], properties={})
    assert "At least one label is required" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        manager.create_node(labels=["Person"], properties={})
    assert "Properties are required" in str(exc_info.value)


def test_find_node_success():
    """ノード検索の成功ケースをテストする。
    
    必要性：
    - ノードの正常な検索を確認
    - 返却値の正確性を検証
    
    十分性：
    - 検索条件の正しい適用
    - 返却されたノードデータの検証
    """
    manager = Neo4jManager()
    
    # テスト用のノードを作成
    test_properties = {"name": "Test Person"}
    node_id = manager.create_node(
        labels=["Person"],
        properties=test_properties
    )
    
    # 作成したノードを検索
    node = manager.find_node(
        labels=["Person"],
        properties=test_properties
    )
    
    assert node is not None
    assert isinstance(node, dict)
    assert "name" in node
    assert node["name"] == "Test Person"


def test_find_node_validation_error():
    """ノード検索の入力検証エラーケースをテストする。
    
    必要性：
    - 無効な検索条件の検出を確認
    - 適切なエラーメッセージの生成を検証
    
    十分性：
    - ラベル未指定のケース
    - プロパティ未指定のケース
    """
    manager = Neo4jManager()
    
    with pytest.raises(ValueError) as exc_info:
        manager.find_node(labels=[], properties={})
    assert "At least one label is required" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        manager.find_node(labels=["Person"], properties={})
    assert "Search properties are required" in str(exc_info.value)


def test_update_node_success():
    """ノード更新の成功ケースをテストする。
    
    必要性：
    - ノードの正常な更新を確認
    - 返却値の正確性を検証
    
    十分性：
    - プロパティの正しい更新
    - 更新結果の検証
    """
    manager = Neo4jManager()
    
    # テスト用のノードを作成
    node_id = manager.create_node(
        labels=["Person"],
        properties={"name": "Original Name"}
    )
    
    # 作成したノードを更新
    success = manager.update_node(
        node_id=node_id,
        properties={"name": "Updated Person"}
    )
    
    assert success is True


def test_update_node_validation_error():
    """ノード更新の入力検証エラーケースをテストする。
    
    必要性：
    - 無効な更新パラメータの検出を確認
    - 適切なエラーメッセージの生成を検証
    
    十分性：
    - ノードID未指定のケース
    - プロパティ未指定のケース
    """
    manager = Neo4jManager()
    
    with pytest.raises(ValueError) as exc_info:
        manager.update_node(node_id="", properties={})
    assert "Node ID is required" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        manager.update_node(node_id="1", properties={})
    assert "Update properties are required" in str(exc_info.value)


def test_create_relationship_success():
    """リレーションシップ作成の成功ケースをテストする。
    
    必要性：
    - リレーションシップの正常な作成を確認
    - 返却値の正確性を検証
    
    十分性：
    - 開始・終了ノードの正しい指定
    - リレーションシップタイプとプロパティの設定
    """
    manager = Neo4jManager()
    
    # テスト用のノードを作成
    start_node_id = manager.create_node(
        labels=["Person"],
        properties={"name": "Person 1"}
    )
    end_node_id = manager.create_node(
        labels=["Person"],
        properties={"name": "Person 2"}
    )
    
    # ノード間にリレーションシップを作成
    success = manager.create_relationship(
        start_node_id=start_node_id,
        end_node_id=end_node_id,
        relationship_type="KNOWS",
        properties={"since": "2024"}
    )
    
    assert success is True


def test_create_relationship_validation_error():
    """リレーションシップ作成の入力検証エラーケースをテストする。
    
    必要性：
    - 無効な入力パラメータの検出を確認
    - 適切なエラーメッセージの生成を検証
    
    十分性：
    - 開始・終了ノード未指定のケース
    - リレーションシップタイプ未指定のケース
    """
    manager = Neo4jManager()
    
    with pytest.raises(ValueError) as exc_info:
        manager.create_relationship(
            start_node_id="",
            end_node_id="2",
            relationship_type="KNOWS"
        )
    assert "Start node ID is required" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        manager.create_relationship(
            start_node_id="1",
            end_node_id="",
            relationship_type="KNOWS"
        )
    assert "End node ID is required" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        manager.create_relationship(
            start_node_id="1",
            end_node_id="2",
            relationship_type=""
        )
    assert "Relationship type is required" in str(exc_info.value)


def test_run_query_success():
    """カスタムクエリ実行の成功ケースをテストする。
    
    必要性：
    - クエリの正常な実行を確認
    - 返却値の正確性を検証
    
    十分性：
    - パラメータ化クエリの実行
    - 結果データの形式検証
    """
    manager = Neo4jManager()
    
    result = manager.run_query(
        "MATCH (n:Person) WHERE n.name = $name RETURN n",
        {"name": "Test Person"}
    )
    
    assert result is not None
    assert isinstance(result, list)


def test_run_query_validation_error():
    """カスタムクエリ実行の入力検証エラーケースをテストする。
    
    必要性：
    - 無効なクエリの検出を確認
    - 適切なエラーメッセージの生成を検証
    
    十分性：
    - クエリ文字列未指定のケース
    """
    manager = Neo4jManager()
    
    with pytest.raises(ValueError) as exc_info:
        manager.run_query("", {})
    assert "Query string is required" in str(exc_info.value)


def test_find_nodes_success():
    """複数ノードの検索の成功ケースをテストする。
    
    必要性：
    - 複数ノードの検索機能の確認
    - 結果の形式と内容の検証
    
    十分性：
    - 複数ノードの作成と検索
    - 結果の完全性確認
    - プロパティの正確性確認
    """
    manager = Neo4jManager()
    
    # テスト用のノードを複数作成
    test_properties1 = {"name": "Test Person 1", "age": 30}
    test_properties2 = {"name": "Test Person 2", "age": 30}
    
    node_id1 = manager.create_node(
        labels=["Person"],
        properties=test_properties1
    )
    node_id2 = manager.create_node(
        labels=["Person"],
        properties=test_properties2
    )
    
    # 年齢が30の全ノードを検索
    nodes = manager.find_nodes(
        labels=["Person"],
        properties={"age": 30}
    )
    
    assert len(nodes) >= 2
    assert any(node["name"] == "Test Person 1" for node in nodes)
    assert any(node["name"] == "Test Person 2" for node in nodes)
    assert all(node["age"] == 30 for node in nodes)


def test_find_nodes_empty_result():
    """存在しないノードの検索ケースをテストする。
    
    必要性：
    - 該当ノードが存在しない場合の動作確認
    - 空の結果の処理確認
    
    十分性：
    - 存在しない条件での検索
    - 戻り値の型と内容の確認
    """
    manager = Neo4jManager()
    
    # 存在しない条件で検索
    nodes = manager.find_nodes(
        labels=["NonExistentLabel"],
        properties={"name": "NonExistent"}
    )
    
    assert isinstance(nodes, list)
    assert len(nodes) == 0


def test_find_nodes_validation_error():
    """入力検証エラーケースをテストする。
    
    必要性：
    - パラメータバリデーションの確認
    - エラーメッセージの検証
    
    十分性：
    - 無効なパラメータパターン
    - エラーメッセージの正確性
    """
    manager = Neo4jManager()
    
    # ラベルが空のケース
    with pytest.raises(ValueError) as exc_info:
        manager.find_nodes(labels=[], properties={"name": "Test"})
    assert "At least one label is required" in str(exc_info.value)
    
    # プロパティが空のケース
    with pytest.raises(ValueError) as exc_info:
        manager.find_nodes(labels=["Person"], properties={})
    assert "Search properties are required" in str(exc_info.value) 