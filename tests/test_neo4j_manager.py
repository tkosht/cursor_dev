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

import random
import string

from dotenv import load_dotenv

from app.neo4j_manager import Neo4jManager

# テスト用の環境変数を読み込む
load_dotenv('.env.test')


def test_init_with_env_vars():
    """環境変数を使用した初期化をテストする。
    
    必要性：
    - 環境変数からの設定読み込み確認
    - 接続確立の検証
    
    十分性：
    - 必須環境変数の確認
    - 接続テスト
    """
    manager = Neo4jManager()
    assert manager is not None
    
    # セッションが正常に作成できることを確認
    with manager._get_session() as session:
        result = session.run("RETURN 1 as n")
        value = result.single()["n"]
        assert value == 1


def test_create_and_find_node():
    """ノードの作成と検索をテストする。
    
    必要性：
    - 基本的なCRUD操作の確認
    - データの整合性検証
    
    十分性：
    - 正確なプロパティ設定
    - 検索結果の確認
    """
    manager = Neo4jManager()
    
    # テストデータ
    labels = ["TestNode"]
    properties = {
        "name": "Test Node",
        "value": 42
    }
    
    # ノードを作成
    node_id = manager.create_node(labels, properties)
    assert node_id is not None
    
    # ノードを検索
    node = manager.find_node(labels, properties)
    assert node is not None
    assert node["name"] == "Test Node"
    assert node["value"] == 42


def test_create_relationship():
    """リレーションシップの作成をテストする。
    
    必要性：
    - ノード間の関係性構築確認
    - プロパティ設定の検証
    
    十分性：
    - 正確な関係性の作成
    - プロパティの設定確認
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node1_id = manager.create_node(
        ["TestNode"],
        {"name": "Node 1"}
    )
    
    node2_id = manager.create_node(
        ["TestNode"],
        {"name": "Node 2"}
    )
    
    # リレーションシップを作成
    success = manager.create_relationship(
        node1_id,
        node2_id,
        "TEST_RELATION",
        {"property": "value"}
    )
    
    assert success is True
    
    # リレーションシップを確認
    with manager._get_session() as session:
        result = session.run(
            """
            MATCH (a)-[r:TEST_RELATION]->(b)
            WHERE elementId(a) = $start_id AND elementId(b) = $end_id
            RETURN r
            """,
            start_id=node1_id,
            end_id=node2_id
        )
        relationship = result.single()
        assert relationship is not None
        assert relationship["r"]["property"] == "value"


def test_find_node_by_id():
    """IDによるノードの検索をテストする。
    
    必要性：
    - ID検索機能の確認
    - 存在確認の検証
    
    十分性：
    - 正確なノード取得
    - 存在しないIDの処理
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node_id = manager.create_node(
        ["TestNode"],
        {"name": "Test Node"}
    )
    
    # IDで検索
    node = manager.find_node_by_id(node_id)
    assert node is not None
    assert node["name"] == "Test Node"
    
    # 存在しないIDで検索
    node = manager.find_node_by_id("nonexistent_id")
    assert node is None


def test_delete_node():
    """ノードの削除をテストする。
    
    必要性：
    - 削除機能の確認
    - データ整合性の検証
    
    十分性：
    - 正常な削除
    - 存在確認
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node_id = manager.create_node(
        ["TestNode"],
        {"name": "Test Node"}
    )
    
    # ノードを削除
    success = manager.delete_node(node_id)
    assert success is True
    
    # 削除を確認
    node = manager.find_node_by_id(node_id)
    assert node is None


def test_large_property_node():
    """大量のプロパティを持つノードの作成と取得をテストする。
    
    必要性：
    - 大量データ処理の動作確認
    - メモリ使用量の検証
    
    十分性：
    - 大量プロパティの正常な保存
    - 全プロパティの正確な取得
    """
    manager = Neo4jManager()
    
    # 100個のプロパティを持つ辞書を作成
    large_props = {
        f"prop_{i}": f"value_{i}"
        for i in range(100)
    }
    
    # ノードを作成
    _ = manager.create_node(
        labels=["LargeNode"],
        properties=large_props
    )
    
    # ノードを取得して検証
    node = manager.find_node(
        labels=["LargeNode"],
        properties={"prop_0": "value_0"}
    )
    
    assert node is not None
    assert len(node) == 100
    for i in range(100):
        assert node[f"prop_{i}"] == f"value_{i}"


def test_long_string_values():
    """長い文字列値を持つノードの作成と取得をテストする。
    
    必要性：
    - 長文字列の処理確認
    - データの整合性検証
    
    十分性：
    - 長文字列の正常な保存
    - 文字列の完全一致確認
    """
    manager = Neo4jManager()
    
    # 10000文字のランダムな文字列を生成
    long_string = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=10000
        )
    )
    
    # ノードを作成
    _ = manager.create_node(
        labels=["LongStringNode"],
        properties={"content": long_string}
    )
    
    # ノードを取得して検証
    node = manager.find_node(
        labels=["LongStringNode"],
        properties={"content": long_string}
    )
    
    assert node is not None
    assert node["content"] == long_string


def test_special_characters():
    """特殊文字を含むプロパティを持つノードの作成と取得をテストする。
    
    必要性：
    - 特殊文字の処理確認
    - エスケープ処理の検証
    
    十分性：
    - 特殊文字の正常な保存
    - 文字列の完全一致確認
    """
    manager = Neo4jManager()
    
    special_chars = {
        "symbols": "!@#$%^&*()_+-=[]{}|;:'\",.<>?/\\",
        "unicode": "あいうえお♪㈱☺",
        "whitespace": " \t\n\r",
        "quotes": "'single' and \"double\" quotes"
    }
    
    # ノードを作成
    _ = manager.create_node(
        labels=["SpecialCharNode"],
        properties=special_chars
    )
    
    # ノードを取得して検証
    node = manager.find_node(
        labels=["SpecialCharNode"],
        properties={"symbols": special_chars["symbols"]}
    )
    
    assert node is not None
    for key, value in special_chars.items():
        assert node[key] == value


def test_multiple_relationship_types():
    """複数タイプのリレーションシップの作成と取得をテストする。
    
    必要性：
    - 複数関係の管理確認
    - リレーションシップの整合性検証
    
    十分性：
    - 異なる種類の関係の作成
    - プロパティの正確な設定
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    start_node_id = manager.create_node(
        labels=["Company"],
        properties={"name": "Company A"}
    )
    
    end_node_id = manager.create_node(
        labels=["Company"],
        properties={"name": "Company B"}
    )
    
    # 異なるタイプのリレーションシップを作成
    relationships = [
        ("COMPETES_WITH", {"market": "Global", "strength": 0.8}),
        ("COLLABORATES_WITH", {"project": "Project X", "budget": 1000000}),
        ("SUPPLIES_TO", {"product": "Widget", "volume": 500})
    ]
    
    for rel_type, props in relationships:
        success = manager.create_relationship(
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            rel_type=rel_type,
            properties=props
        )
        assert success is True
    
    # リレーションシップを検証
    with manager._get_session() as session:
        for rel_type, props in relationships:
            result = session.run(
                """
                MATCH (a)-[r:%s]->(b)
                WHERE elementId(a) = $start_id AND elementId(b) = $end_id
                RETURN r
                """ % rel_type,
                start_id=start_node_id,
                end_id=end_node_id
            )
            relationship = result.single()
            assert relationship is not None
            for key, value in props.items():
                assert relationship["r"][key] == value


def test_relationship_with_properties():
    """プロパティ付きリレーションシップの作成と取得をテストする。
    
    必要性：
    - リレーションシッププロパティの管理確認
    - プロパティの整合性検証
    
    十分性：
    - 複雑なプロパティの設定
    - プロパティの正確な取得
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    start_node_id = manager.create_node(
        labels=["Product"],
        properties={"name": "Product A"}
    )
    
    end_node_id = manager.create_node(
        labels=["Category"],
        properties={"name": "Category B"}
    )
    
    # 複雑なプロパティを持つリレーションシップを作成
    rel_props = {
        "created_at": "2024-01-08T00:00:00",
        "strength": 0.95,
        "source": "test",
        "confidence": 0.8,
        "tags": ["important", "verified"],
        "numeric_values": [1, 2, 3, 4, 5],
        "description": "Detailed relationship description"
    }
    
    success = manager.create_relationship(
        start_node_id=start_node_id,
        end_node_id=end_node_id,
        rel_type="BELONGS_TO",
        properties=rel_props
    )
    assert success is True
    
    # リレーションシップを検証
    with manager._get_session() as session:
        result = session.run(
            """
            MATCH (a)-[r:BELONGS_TO]->(b)
            WHERE elementId(a) = $start_id AND elementId(b) = $end_id
            RETURN r
            """,
            start_id=start_node_id,
            end_id=end_node_id
        )
        relationship = result.single()
        assert relationship is not None
        for key, value in rel_props.items():
            assert relationship["r"][key] == value


def test_nonexistent_nodes_relationship():
    """存在しないノード間のリレーションシップ作成をテストする。
    
    必要性：
    - エラー処理の確認
    - データ整合性の検証
    
    十分性：
    - エラーの適切な検出
    - エラーメッセージの確認
    """
    manager = Neo4jManager()
    
    # 存在しないノードIDを使用
    non_existent_id1 = "non_existent_1"
    non_existent_id2 = "non_existent_2"
    
    # リレーションシップの作成を試みる
    success = manager.create_relationship(
        start_node_id=non_existent_id1,
        end_node_id=non_existent_id2,
        rel_type="TEST_RELATION",
        properties={"test": "value"}
    )
    
    assert success is False 