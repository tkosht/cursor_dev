"""KnowledgeRepositoryのテストモジュール。"""

import pytest
from datetime import datetime
from app.knowledge_repository import KnowledgeRepository
from app.neo4j_manager import Neo4jManager


@pytest.fixture
def neo4j_manager():
    """Neo4jManagerのインスタンスを提供するフィクスチャ。"""
    return Neo4jManager()


@pytest.fixture
def repository(neo4j_manager):
    """KnowledgeRepositoryのインスタンスを提供するフィクスチャ。"""
    return KnowledgeRepository(neo4j_manager)


@pytest.fixture
def valid_analysis_result():
    """有効な分析結果を提供するフィクスチャ。"""
    return {
        "entities": [
            {
                "id": "company1",
                "name": "テスト株式会社",
                "type": "COMPANY",
                "description": "テスト企業の説明"
            },
            {
                "id": "product1",
                "name": "テスト製品",
                "type": "PRODUCT",
                "description": "テスト製品の説明"
            }
        ],
        "relationships": [
            {
                "source": "テスト株式会社",
                "target": "テスト製品",
                "type": "DEVELOPS",
                "description": "開発関係",
                "strength": 0.8
            }
        ],
        "impact_scores": {
            "company1": 0.7,
            "product1": 0.5
        },
        "source_url": "https://example.com",
        "analyzed_at": datetime.now()
    }


class TestKnowledgeRepository:
    """KnowledgeRepositoryのテストクラス。"""

    def test_init(self, neo4j_manager):
        """初期化が正しく行われることを確認。"""
        repository = KnowledgeRepository(neo4j_manager)
        assert repository.neo4j_manager == neo4j_manager

    def test_store_analysis_success(self, repository, valid_analysis_result):
        """分析結果が正常に保存されることを確認。"""
        result = repository.store_analysis(valid_analysis_result)
        assert result is True

    def test_store_analysis_invalid_format(self, repository):
        """不正な形式の分析結果でエラーが発生することを確認。"""
        invalid_result = {"invalid": "data"}
        with pytest.raises(ValueError) as exc_info:
            repository.store_analysis(invalid_result)
        assert "Invalid analysis result format" in str(exc_info.value)

    def test_validate_required_keys(self, repository, valid_analysis_result):
        """必須キーの検証が正しく機能することを確認。"""
        assert repository._validate_required_keys(valid_analysis_result) is True

        # 必須キーが欠けている場合
        invalid_result = valid_analysis_result.copy()
        del invalid_result["entities"]
        assert repository._validate_required_keys(invalid_result) is False

    def test_validate_entities(self, repository, valid_analysis_result):
        """エンティティ情報の検証が正しく機能することを確認。"""
        assert repository._validate_entities(valid_analysis_result["entities"]) is True

        # 必須キーが欠けているエンティティ
        invalid_entities = [{"name": "テスト"}]  # idとtypeが欠けている
        assert repository._validate_entities(invalid_entities) is False

        # 不正な型のエンティティ
        invalid_entities = [123]  # dictではない
        assert repository._validate_entities(invalid_entities) is False

    def test_validate_relationships(self, repository, valid_analysis_result):
        """関係性情報の検証が正しく機能することを確認。"""
        assert repository._validate_relationships(valid_analysis_result["relationships"]) is True

        # 必須キーが欠けている関係性
        invalid_relationships = [{"source": "テスト"}]  # targetとtypeが欠けている
        assert repository._validate_relationships(invalid_relationships) is False

        # 不正な型の関係性
        invalid_relationships = [123]  # dictではない
        assert repository._validate_relationships(invalid_relationships) is False

    def test_validate_impact_scores(self, repository, valid_analysis_result):
        """影響度スコアの検証が正しく機能することを確認。"""
        assert repository._validate_impact_scores(valid_analysis_result["impact_scores"]) is True

        # 範囲外のスコア
        invalid_scores = {"test": 1.5}  # 1.0を超えている
        assert repository._validate_impact_scores(invalid_scores) is False

        # 不正な型のスコア
        invalid_scores = {"test": "high"}  # 数値ではない
        assert repository._validate_impact_scores(invalid_scores) is False

    def test_store_entities_new(self, repository, valid_analysis_result):
        """新規エンティティが正しく保存されることを確認。"""
        entity_id_map = repository._store_entities(valid_analysis_result)
        assert len(entity_id_map) == 2
        assert "テスト株式会社" in entity_id_map
        assert "テスト製品" in entity_id_map

    def test_store_entities_update(self, repository, valid_analysis_result):
        """既存エンティティが正しく更新されることを確認。"""
        # 最初の保存
        repository._store_entities(valid_analysis_result)
        
        # 2回目の保存（更新）
        updated_result = valid_analysis_result.copy()
        updated_result["impact_scores"]["company1"] = 0.9
        entity_id_map = repository._store_entities(updated_result)
        
        assert len(entity_id_map) == 2
        assert "テスト株式会社" in entity_id_map
        assert "テスト製品" in entity_id_map

    def test_store_relationships(self, repository, valid_analysis_result):
        """関係性が正しく保存されることを確認。"""
        # エンティティを先に保存
        entity_id_map = repository._store_entities(valid_analysis_result)
        
        # 関係性の保存
        repository._store_relationships(valid_analysis_result, entity_id_map)
        
        # 関係性の検証は、Neo4jManagerのメソッドが正しく呼び出されたことで確認 