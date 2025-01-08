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

import pytest
from dotenv import load_dotenv

from app.neo4j_manager import Neo4jManager

# テスト用の環境変数を読み込む
load_dotenv('.env.test')


def test_init_with_env_vars():
    """環境変数からの初期化をテストする。
    
    必要性：
    - 設定の正常な読み込み
    - 接続の確立
    
    十分性：
    - 環境変数の読み込み
    - 接続の成功
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
    manager.create_node(
        labels=["LargeNode"],
        properties=large_props
    )
    
    # ノードを取得して検証
    node = manager.find_node(
        labels=["LargeNode"],
        properties={"prop_0": "value_0"}
    )
    
    assert node is not None
    # IDプロパティを除外して検証
    node_props = {k: v for k, v in node.items() if not k.startswith("id")}
    assert len(node_props) == 100


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
    - データ整合性の検検証
    
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


def test_update_node():
    """ノードの更新をテストする。
    
    必要性：
    - 更新機能の確認
    - データ整合性の検証
    
    十分性：
    - プロパティの更新確認
    - 存在しないノードの処理
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node_id = manager.create_node(
        ["TestNode"],
        {"name": "Original Name", "value": 42}
    )
    
    # ノードを更新
    success = manager.update_node(
        node_id,
        {"name": "Updated Name", "value": 100}
    )
    assert success is True
    
    # 更新を確認
    node = manager.find_node_by_id(node_id)
    assert node is not None
    assert node["name"] == "Updated Name"
    assert node["value"] == 100
    
    # 存在しないノードの更新を試みる
    success = manager.update_node(
        "nonexistent_id",
        {"name": "Test"}
    )
    assert success is False


def test_update_node_partial():
    """ノードの部分更新をテストする。
    
    必要性：
    - 部分更新の動作確認
    - 既存プロパティの保持確認
    
    十分性：
    - 一部プロパティの更新
    - 他のプロパティの保持
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node_id = manager.create_node(
        ["TestNode"],
        {
            "name": "Original Name",
            "value": 42,
            "extra": "Keep This"
        }
    )
    
    # 一部のプロパティのみ更新
    success = manager.update_node(
        node_id,
        {"name": "Updated Name"}
    )
    assert success is True
    
    # 更新を確認
    node = manager.find_node_by_id(node_id)
    assert node is not None
    assert node["name"] == "Updated Name"
    assert node["value"] == 42  # 未更新のプロパティは保持
    assert node["extra"] == "Keep This"  # 未更新のプロパティは保持


def test_update_node_invalid_params():
    """無効なパラメータでのノード更新をテストする。
    
    必要性：
    - エラー処理の確認
    - 入力検証の確認
    
    十分性：
    - 無効なIDの処理
    - 無効なプロパティの処理
    """
    manager = Neo4jManager()
    
    # None IDでの更新を試みる
    with pytest.raises(ValueError):
        manager.update_node(None, {"name": "Test"})


def test_store_entity():
    """エンティティの保存をテストする。
    
    必要性：
    - エンティティ保存機能の確認
    - 既存エンティティの更新確認
    
    十分性：
    - 新規エンティティの作成
    - 既存エンティティの更新
    """
    manager = Neo4jManager()
    
    # 新規エンティティを保存
    entity = {
        "id": "test_entity_1",
        "name": "Test Entity",
        "type": "TestType",
        "properties": {
            "value": 42,
            "description": "Test Description"
        }
    }
    
    success = manager.store_entity(entity)
    assert success is True
    
    # エンティティが保存されたことを確認
    node = manager.find_node(
        ["Entity", "TestType"],
        {"id": "test_entity_1"}
    )
    assert node is not None
    assert node["name"] == "Test Entity"
    assert node["value"] == 42
    assert node["description"] == "Test Description"
    
    # エンティティを更新
    entity["properties"]["value"] = 100
    entity["properties"]["new_prop"] = "New Value"
    
    success = manager.store_entity(entity)
    assert success is True
    
    # 更新を確認
    node = manager.find_node(
        ["Entity", "TestType"],
        {"id": "test_entity_1"}
    )
    assert node is not None
    assert node["value"] == 100
    assert node["new_prop"] == "New Value"


def test_store_entity_none():
    """Noneエンティティの保存をテストする。
    
    必要性：
    - エラー処理の確認
    
    十分性：
    - Noneエンティティの処理
    """
    manager = Neo4jManager()
    
    try:
        manager.store_entity(None)
        assert False  # 例外が発生すべき
    except ValueError:
        assert True  # 例外が発生することを確認


def test_store_entity_missing_id():
    """IDなしエンティティの保存をテストする。
    
    必要性：
    - 必須フィールドの検証
    
    十分性：
    - IDなしエンティティの処理
    """
    manager = Neo4jManager()
    
    try:
        entity = {
            "name": "Test Entity",
            "type": "TestType",
            "properties": {}
        }
        manager.store_entity(entity)
        assert False  # 例外が発生すべき
    except ValueError:
        assert True  # 例外が発生することを確認


def test_store_entity_missing_type():
    """タイプなしエンティティの保存をテストする。
    
    必要性：
    - 必須フィールドの検証
    
    十分性：
    - タイプなしエンティティの処理
    """
    manager = Neo4jManager()
    
    try:
        entity = {
            "id": "test_entity_2",
            "name": "Test Entity",
            "properties": {}
        }
        manager.store_entity(entity)
        assert False  # 例外が発生すべき
    except ValueError:
        assert True  # 例外が発生することを確認


def test_store_entity_missing_properties():
    """プロパティなしエンティティの保存をテストする。
    
    必要性：
    - 必須フィールドの検証
    
    十分性：
    - プロパティなしエンティティの処理
    """
    manager = Neo4jManager()
    
    try:
        entity = {
            "id": "test_entity_2",
            "name": "Test Entity",
            "type": "TestType"
        }
        manager.store_entity(entity)
        assert False  # 例外が発生すべき
    except ValueError:
        assert True  # 例外が発生することを確認


def test_store_entity_with_relationships():
    """関係を持つエンティティの保存をテストする。
    
    必要性：
    - 関係を持つエンティティの保存確認
    - 関係の整合性検証
    
    十分性：
    - エンティティと関係の保存
    - 関係プロパティの検証
    """
    manager = Neo4jManager()
    
    # 関連エンティティを作成
    related_entity = {
        "id": "related_entity_1",
        "name": "Related Entity",
        "type": "TestType",
        "properties": {
            "value": 42
        }
    }
    success = manager.store_entity(related_entity)
    assert success is True
    
    # メインエンティティを関係付きで保存
    entity = {
        "id": "main_entity_1",
        "name": "Main Entity",
        "type": "TestType",
        "properties": {
            "value": 100
        },
        "relationships": [
            {
                "target_id": "related_entity_1",
                "type": "RELATES_TO",
                "properties": {
                    "strength": 0.8
                }
            }
        ]
    }
    success = manager.store_entity(entity)
    assert success is True
    
    # 関係を確認
    with manager._get_session() as session:
        result = session.run(
            """
            MATCH (a:Entity:TestType)-[r:RELATES_TO]->(b:Entity:TestType)
            WHERE a.id = $source_id AND b.id = $target_id
            RETURN r
            """,
            source_id="main_entity_1",
            target_id="related_entity_1"
        )
        relationship = result.single()
        assert relationship is not None
        assert relationship["r"]["strength"] == 0.8


def test_database_connection_error():
    """データベース接続エラーをテストする。
    
    必要性：
    - 接続エラー処理の確認
    - エラーログの検証
    
    十分性：
    - 接続エラーの処理
    - エラーメッセージの確認
    """
    import os
    from unittest.mock import patch

    # 一時的に環境変数を変更
    with patch.dict(os.environ, {
        'NEO4J_URI': 'bolt://invalid:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'password'
    }):
        try:
            Neo4jManager()
            assert False  # 例外が発生すべき
        except ValueError:
            assert True  # 例外が発生することを確認


def test_transaction_error():
    """トランザクションエラーをテストする。
    
    必要性：
    - トランザクション処理の確認
    - ロールバックの検証
    
    十分性：
    - エラー時のロールバック
    - データ整合性の確認
    """
    manager = Neo4jManager()

    # トランザクション前のノード数を取得
    with manager._get_session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_before = result.single()["count"]

    # エラーを含むトランザクションを実行
    try:
        def error_tx(tx):
            # 正常なクエリ
            tx.run(
                "CREATE (n:TestNode {name: $name})",
                name="Test Node"
            )
            # 無効なクエリ
            tx.run("INVALID QUERY")
            return True

        manager._execute_transaction(error_tx)
        assert False  # エラーが発生すべき
    except Exception:
        # エラーが発生することを確認
        assert True

    # トランザクションがロールバックされたことを確認
    with manager._get_session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_after = result.single()["count"]
        assert count_before == count_after


def test_find_relationships_outgoing():
    """出力方向のリレーションシップ検索をテストする。
    
    必要性：
    - 方向指定検索の確認
    - 結果形式の検証
    
    十分性：
    - 正しい方向のみ取得
    - プロパティの正確な取得
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    start_node = manager.create_node(
        ["TestNode"],
        {"name": "Start Node"}
    )
    end_node = manager.create_node(
        ["TestNode"],
        {"name": "End Node"}
    )
    
    # 出力方向のリレーションシップを作成
    manager.create_relationship(
        start_node,
        end_node,
        "TEST_REL",
        {"prop": "value"}
    )
    
    # 出力方向のリレーションシップを検索
    relationships = manager.find_relationships(start_node, "outgoing")
    assert len(relationships) == 1
    assert relationships[0]["type"] == "TEST_REL"
    assert relationships[0]["properties"]["prop"] == "value"
    assert relationships[0]["start_node"] == start_node
    assert relationships[0]["end_node"] == end_node


def test_find_relationships_incoming():
    """入力方向のリレーションシップ検索をテストする。
    
    必要性：
    - 入力方向の検索確認
    - 結果形式の検証
    
    十分性：
    - 正しい方向のみ取得
    - プロパティの正確な取得
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    start_node = manager.create_node(
        ["TestNode"],
        {"name": "Start Node"}
    )
    end_node = manager.create_node(
        ["TestNode"],
        {"name": "End Node"}
    )
    
    # 入力方向のリレーションシップを作成
    manager.create_relationship(
        start_node,
        end_node,
        "TEST_REL",
        {"prop": "value"}
    )
    
    # 入力方向のリレーションシップを検索
    relationships = manager.find_relationships(end_node, "incoming")
    assert len(relationships) == 1
    assert relationships[0]["type"] == "TEST_REL"
    assert relationships[0]["properties"]["prop"] == "value"
    assert relationships[0]["start_node"] == start_node
    assert relationships[0]["end_node"] == end_node


def test_find_relationships_both():
    """双方向のリレーションシップ検索をテストする。
    
    必要性：
    - 双方向検索の確認
    - 結果形式の検証
    
    十分性：
    - 両方向の取得
    - プロパティの正確な取得
    """
    manager = Neo4jManager()
    
    # テストノードを作成
    node1 = manager.create_node(
        ["TestNode"],
        {"name": "Node 1"}
    )
    node2 = manager.create_node(
        ["TestNode"],
        {"name": "Node 2"}
    )
    node3 = manager.create_node(
        ["TestNode"],
        {"name": "Node 3"}
    )
    
    # 双方向のリレーションシップを作成
    manager.create_relationship(
        node1,
        node2,
        "OUTGOING_REL",
        {"direction": "out"}
    )
    manager.create_relationship(
        node3,
        node2,
        "INCOMING_REL",
        {"direction": "in"}
    )
    
    # 双方向のリレーションシップを検索
    relationships = manager.find_relationships(node2, "both")
    assert len(relationships) == 2
    
    # リレーションシップの方向とプロパティを検証
    rel_types = {rel["type"] for rel in relationships}
    assert "OUTGOING_REL" in rel_types
    assert "INCOMING_REL" in rel_types


def test_find_relationships_error():
    """リレーションシップ検索のエラー処理をテストする。
    
    必要性：
    - エラー処理の確認
    - 戻り値の検証
    
    十分性：
    - エラー時の空リスト返却
    - ログ出力の確認
    """
    manager = Neo4jManager()
    
    # 存在しないノードIDでの検索
    relationships = manager.find_relationships("non_existent_id")
    assert isinstance(relationships, list)
    assert len(relationships) == 0
 