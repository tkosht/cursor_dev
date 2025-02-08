"""Neo4jとの結合テストモジュール"""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from app.exceptions import DatabaseError, ValidationError
from app.neo4j_manager import Neo4jManager


class TestNeo4jIntegration(unittest.TestCase):
    """Neo4jとの結合テスト"""

    def setUp(self):
        """テストの前準備"""
        self.neo4j_user = os.getenv("NEO4J_USER")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.neo4j_uri = os.getenv("NEO4J_URI")

        if not all([self.neo4j_user, self.neo4j_password, self.neo4j_uri]):
            self.skipTest("Neo4j credentials not found in environment variables")

        self.neo4j = Neo4jManager(
            uri=self.neo4j_uri,
            user=self.neo4j_user,
            password=self.neo4j_password
        )

        # 実際のデータ構造に近いテストデータ
        self.test_entities = [
            {
                "id": "company_google",
                "name": "Google",
                "type": "COMPANY",
                "description": "世界的なテクノロジー企業",
                "properties": {
                    "market_impact": 0.95,
                    "sector": "Technology",
                    "source": "test",
                    "analyzed_at": datetime.now().isoformat()
                }
            },
            {
                "id": "product_gemini",
                "name": "Gemini",
                "type": "PRODUCT",
                "description": "次世代AI言語モデル",
                "properties": {
                    "market_impact": 0.85,
                    "category": "AI/ML",
                    "source": "test",
                    "analyzed_at": datetime.now().isoformat()
                }
            },
            {
                "id": "trend_ai",
                "name": "AI adoption",
                "type": "TREND",
                "description": "企業のAI導入トレンド",
                "properties": {
                    "market_impact": 0.9,
                    "category": "Technology Trend",
                    "source": "test",
                    "analyzed_at": datetime.now().isoformat()
                }
            }
        ]

        self.test_relationships = [
            {
                "source": "company_google",
                "target": "product_gemini",
                "type": "DEVELOPS",
                "properties": {
                    "strength": 0.9,
                    "description": "開発・提供関係",
                    "source": "test",
                    "analyzed_at": datetime.now().isoformat()
                }
            },
            {
                "source": "company_google",
                "target": "trend_ai",
                "type": "PARTICIPATES",
                "properties": {
                    "strength": 0.85,
                    "description": "トレンドへの参画",
                    "source": "test",
                    "analyzed_at": datetime.now().isoformat()
                }
            }
        ]

    def tearDown(self):
        """テストの後片付け"""
        try:
            # テストで作成したノードとリレーションシップを削除
            self.neo4j.execute_query("""
                MATCH (n)
                WHERE n.source = 'test'
                DETACH DELETE n
            """)
        finally:
            self.neo4j.close()

    def test_create_and_find_nodes(self):
        """ノードの作成と検索テスト"""
        try:
            # ノードの作成
            node_ids = []
            for entity in self.test_entities:
                node_id = self.neo4j.create_node(
                    labels=[entity["type"]],
                    properties=entity["properties"]
                )
                self.assertIsNotNone(node_id)
                node_ids.append(node_id)

            # ノードの検索（複数の条件で）
            for entity in self.test_entities:
                # 名前での検索
                found_node = self.neo4j.find_node(
                    labels=[entity["type"]],
                    properties={"name": entity["name"]}
                )
                self.assertIsNotNone(found_node)
                self.assertEqual(found_node["name"], entity["name"])

                # 市場影響度での検索
                found_nodes = self.neo4j.find_nodes(
                    labels=[entity["type"]],
                    properties={"market_impact": {"$gt": 0.8}}
                )
                self.assertTrue(len(found_nodes) > 0)

        except DatabaseError as e:
            self.fail(f"Database error: {str(e)}")
        except ValidationError as e:
            self.fail(f"Validation error: {str(e)}")

    def test_create_and_find_relationships(self):
        """リレーションシップの作成と検索テスト"""
        try:
            # ノードの作成
            for entity in self.test_entities:
                self.neo4j.create_node(
                    labels=[entity["type"]],
                    properties=entity["properties"]
                )

            # リレーションシップの作成
            for rel in self.test_relationships:
                success = self.neo4j.create_relationship(
                    start_node_id=rel["source"],
                    end_node_id=rel["target"],
                    relationship_type=rel["type"],
                    properties=rel["properties"]
                )
                self.assertTrue(success)

            # 複数の条件でリレーションシップを検索
            # 1. タイプによる検索
            develops_rels = self.neo4j.find_relationships(
                relationship_type="DEVELOPS"
            )
            self.assertTrue(len(develops_rels) > 0)

            # 2. 強度による検索
            strong_rels = self.neo4j.find_relationships(
                properties={"strength": {"$gt": 0.8}}
            )
            self.assertTrue(len(strong_rels) > 0)

            # 3. パスの検索
            paths = self.neo4j.execute_query("""
                MATCH path = (c:COMPANY)-[r]->(t:TREND)
                WHERE c.source = 'test'
                RETURN path
            """)
            self.assertTrue(len(paths) > 0)

        except DatabaseError as e:
            self.fail(f"Database error: {str(e)}")
        except ValidationError as e:
            self.fail(f"Validation error: {str(e)}")

    def test_batch_operations(self):
        """バッチ操作のテスト"""
        try:
            # ノードのバッチ作成
            node_ids = self.neo4j.create_nodes_batch(
                nodes=[
                    {
                        "labels": [entity["type"]],
                        "properties": entity["properties"]
                    }
                    for entity in self.test_entities
                ]
            )
            self.assertEqual(len(node_ids), len(self.test_entities))

            # 複数条件でのバッチ検索
            queries = [
                {
                    "labels": ["COMPANY"],
                    "properties": {"sector": "Technology"}
                },
                {
                    "labels": ["PRODUCT"],
                    "properties": {"category": "AI/ML"}
                },
                {
                    "labels": ["TREND"],
                    "properties": {"market_impact": {"$gt": 0.8}}
                }
            ]
            found_nodes = self.neo4j.find_nodes_batch(queries=queries)
            self.assertTrue(len(found_nodes) > 0)

            # リレーションシップのバッチ作成
            success = self.neo4j.create_relationships_batch(
                relationships=[
                    {
                        "start_node_id": rel["source"],
                        "end_node_id": rel["target"],
                        "type": rel["type"],
                        "properties": rel["properties"]
                    }
                    for rel in self.test_relationships
                ]
            )
            self.assertTrue(success)

        except DatabaseError as e:
            self.fail(f"Database error: {str(e)}")
        except ValidationError as e:
            self.fail(f"Validation error: {str(e)}")

    def _test_normal_transaction(self):
        """正常なトランザクションのテスト"""
        with self.neo4j.transaction() as tx:
            # 1. ノードの作成
            for entity in self.test_entities:
                node_id = tx.create_node(
                    labels=[entity["type"]],
                    properties=entity["properties"]
                )
                self.assertIsNotNone(node_id)

            # 2. リレーションシップの作成
            for rel in self.test_relationships:
                success = tx.create_relationship(
                    start_node_id=rel["source"],
                    end_node_id=rel["target"],
                    relationship_type=rel["type"],
                    properties=rel["properties"]
                )
                self.assertTrue(success)

    def _verify_created_nodes(self):
        """作成されたノードの検証"""
        for entity in self.test_entities:
            found_node = self.neo4j.find_node(
                labels=[entity["type"]],
                properties={"name": entity["name"]}
            )
            self.assertIsNotNone(found_node)

    def _test_rollback(self):
        """ロールバックのテスト"""
        try:
            with self.neo4j.transaction() as tx:
                # 正常なノード作成
                node_id = tx.create_node(
                    labels=["TEST"],
                    properties={"name": "test_node", "source": "test"}
                )
                self.assertIsNotNone(node_id)

                # エラーを発生させる
                raise ValueError("Intentional error for rollback test")
        except ValueError:
            # ロールバックされていることを確認
            found_node = self.neo4j.find_node(
                labels=["TEST"],
                properties={"name": "test_node"}
            )
            self.assertIsNone(found_node)

    def test_transaction_management(self):
        """トランザクション管理のテスト"""
        try:
            # 1. 正常なトランザクションのテスト
            self._test_normal_transaction()

            # 2. データが正しく保存されていることを確認
            self._verify_created_nodes()

            # 3. ロールバックのテスト
            self._test_rollback()

        except DatabaseError as e:
            self.fail(f"Database error: {str(e)}")
        except ValidationError as e:
            self.fail(f"Validation error: {str(e)}")

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 1. 無効なプロパティでのノード作成
        with self.assertRaises(ValidationError):
            self.neo4j.create_node(
                labels=["TEST"],
                properties={"invalid": None}
            )

        # 2. 存在しないノードへのリレーションシップ作成
        with self.assertRaises(DatabaseError):
            self.neo4j.create_relationship(
                start_node_id="non_existent",
                end_node_id="non_existent",
                relationship_type="TEST",
                properties={}
            )

        # 3. 無効なクエリ実行
        with self.assertRaises(DatabaseError):
            self.neo4j.execute_query("INVALID QUERY")

        # 4. エラーからの回復
        try:
            # エラー発生
            with self.assertRaises(DatabaseError):
                self.neo4j.execute_query("INVALID QUERY")

            # 回復確認（正常なクエリが実行できる）
            result = self.neo4j.execute_query(
                "MATCH (n) RETURN count(n) as count"
            )
            self.assertIsNotNone(result)

        except Exception as e:
            self.fail(f"Error recovery failed: {str(e)}")

    def test_concurrent_operations(self):
        """並行操作のテスト"""
        def create_and_relate(entity, related_entities):
            try:
                # 1. エンティティの作成
                node_id = self.neo4j.create_node(
                    labels=[entity["type"]],
                    properties=entity["properties"]
                )

                # 2. 関連エンティティとのリレーションシップ作成
                relationships = []
                for related in related_entities:
                    rel_success = self.neo4j.create_relationship(
                        start_node_id=node_id,
                        end_node_id=related["id"],
                        relationship_type="RELATES_TO",
                        properties={
                            "strength": 0.7,
                            "source": "test",
                            "analyzed_at": datetime.now().isoformat()
                        }
                    )
                    relationships.append(rel_success)

                return True, entity["id"], None

            except Exception as e:
                return False, entity["id"], str(e)

        try:
            results = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_entity = {
                    executor.submit(
                        create_and_relate,
                        entity,
                        [e for e in self.test_entities if e != entity]
                    ): entity["id"]
                    for entity in self.test_entities
                }

                for future in as_completed(future_to_entity):
                    success, entity_id, error = future.result()
                    results.append({
                        "entity_id": entity_id,
                        "success": success,
                        "error": error
                    })

            # 結果の検証
            self.assertEqual(len(results), len(self.test_entities))
            successful_results = [r for r in results if r["success"]]
            self.assertGreater(len(successful_results), 0)

        except Exception as e:
            self.fail(f"Concurrent operations test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main() 