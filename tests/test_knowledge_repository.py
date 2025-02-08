"""KnowledgeRepositoryのテストモジュール。"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.exceptions import DatabaseError, Neo4jError, ValidationError
from app.knowledge_repository import KnowledgeRepository
from app.neo4j_manager import Neo4jManager


@pytest.fixture
def neo4j_manager():
    """Neo4jManagerのモックを生成するフィクスチャ。"""
    manager = MagicMock(spec=Neo4jManager)
    manager.uri = "bolt://localhost:7687"
    manager.username = "neo4j"
    manager.password = "password"
    return manager


@pytest.fixture
def knowledge_repository(neo4j_manager):
    """KnowledgeRepositoryのインスタンスを生成するフィクスチャ。"""
    return KnowledgeRepository(neo4j_manager)


def test_init(knowledge_repository):
    """初期化のテストを行う。"""
    assert isinstance(knowledge_repository, KnowledgeRepository)
    assert hasattr(knowledge_repository, 'neo4j_manager')


def test_store_analysis_success(knowledge_repository, neo4j_manager):
    """分析結果の保存が成功するケースをテストする。"""
    analysis_result = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        }
    }

    # モックの設定
    neo4j_manager.begin_transaction.return_value = None
    neo4j_manager.commit_transaction.return_value = None
    neo4j_manager.create_entity_node.return_value = {"id": "1"}

    # テスト実行
    knowledge_repository.store_analysis(analysis_result)

    # 検証
    neo4j_manager.begin_transaction.assert_called_once()
    neo4j_manager.commit_transaction.assert_called_once()
    assert neo4j_manager.create_entity_node.call_count == 1


def test_store_analysis_invalid_format(knowledge_repository):
    """不正な形式の分析結果を保存しようとした場合のテストを行う。"""
    invalid_result = {
        "entities": "invalid",  # リストではない
        "relationships": [],
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository.store_analysis(invalid_result)


def test_validate_analysis_result_success(knowledge_repository):
    """分析結果の検証が成功するケースをテストする。"""
    valid_result = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        }
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_analysis_result(valid_result) is None


def test_validate_analysis_result_missing_keys(knowledge_repository):
    """必須キーが欠けている分析結果の検証をテストする。"""
    invalid_result = {
        "entities": [],
        # relationshipsが欠けている
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_analysis_result(invalid_result)


def test_validate_entities_success(knowledge_repository):
    """エンティティの検証が成功するケースをテストする。"""
    valid_entities = [
        {
            "id": "1",
            "name": "エンティティ1",
            "type": "TYPE1"
        }
    ]

    # 検証が成功することを確認
    assert knowledge_repository._validate_entities(valid_entities) is None


def test_validate_entities_invalid_format(knowledge_repository):
    """不正な型のエンティティフィールドの検証をテストする。"""
    invalid_result = {
        "entities": "invalid",  # 文字列
        "relationships": [],
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_entities(invalid_result)


def test_validate_relationships_success(knowledge_repository):
    """リレーションシップの検証が成功するケースをテストする。"""
    valid_relationships = [
        {
            "source": "1",
            "target": "2",
            "type": "RELATED_TO"
        }
    ]

    # 検証が成功することを確認
    assert knowledge_repository._validate_relationships(valid_relationships) is None


def test_validate_relationships_invalid_format(knowledge_repository):
    """不正な型のリレーションシップフィールドの検証をテストする。"""
    invalid_relationships = [
        {
            "source": "1",
            # targetが欠けている
            "type": "RELATED_TO"
        }
    ]

    with pytest.raises(ValidationError):
        knowledge_repository._validate_relationships(invalid_relationships)


def test_validate_impact_scores_success(knowledge_repository):
    """インパクトスコアの検証が成功するケースをテストする。"""
    valid_scores = {
        "1": 0.8,
        "2": 0.6
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_impact_scores(valid_scores) is None


def test_validate_impact_scores_invalid_range(knowledge_repository):
    """範囲外のインパクトスコアの検証をテストする。"""
    invalid_scores = {
        "1": 1.5,  # 1.0を超えている
        "2": -0.5  # 0.0未満
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores(invalid_scores)


def test_validate_impact_scores_boundary(knowledge_repository):
    """境界値のインパクトスコアの検証をテストする。"""
    boundary_scores = {
        "1": 1.0,  # 最大値
        "2": 0.0   # 最小値
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_impact_scores(boundary_scores) is None


def test_validate_impact_scores_invalid_type(knowledge_repository):
    """不正な型のインパクトスコアの検証をテストする。"""
    invalid_scores = {
        "1": "0.8",  # 文字列
        "2": None    # None
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores(invalid_scores)


def test_validate_impact_scores_invalid_dict_type(knowledge_repository):
    """不正な辞書型のインパクトスコアの検証をテストする。"""
    invalid_scores = [0.8, 0.6]  # リスト

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores(invalid_scores)


def test_validate_impact_scores_invalid_id(knowledge_repository):
    """不正なIDのインパクトスコアの検証をテストする。"""
    invalid_scores = {
        1: 0.8,      # 数値のキー
        None: 0.6    # Noneのキー
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores(invalid_scores)


def test_store_entities_success(knowledge_repository, neo4j_manager):
    """エンティティの保存が成功するケースをテストする。"""
    entities = [
        {
            "id": "1",
            "name": "エンティティ1",
            "type": "TYPE1"
        }
    ]

    # モックの設定
    neo4j_manager.create_entity_node.return_value = {"id": "1"}

    # テスト実行
    knowledge_repository._store_entities(entities)

    # 検証
    neo4j_manager.create_entity_node.assert_called_once_with(
        entity_id="1",
        entity_type="TYPE1",
        properties={"name": "エンティティ1"}
    )


def test_store_relationships_success(knowledge_repository, neo4j_manager):
    """リレーションシップの保存が成功するケースをテストする。"""
    relationships = [
        {
            "source": "1",
            "target": "2",
            "type": "RELATED_TO"
        }
    ]

    # モックの設定
    neo4j_manager.create_relationship.return_value = None

    # テスト実行
    knowledge_repository._store_relationships(relationships)

    # 検証
    neo4j_manager.create_relationship.assert_called_once_with(
        source_id="1",
        target_id="2",
        relationship_type="RELATED_TO",
        properties={}
    )


def test_store_analysis_duplicate_entities(knowledge_repository, neo4j_manager):
    """重複するエンティティの保存をテストする。"""
    analysis_result = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"},
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}  # 重複
        ],
        "relationships": [],
        "impact_scores": {}
    }

    # モックの設定
    neo4j_manager.create_entity_node.return_value = {"id": "1"}

    # テスト実行
    knowledge_repository.store_analysis(analysis_result)

    # 検証：重複は1回だけ保存される
    assert neo4j_manager.create_entity_node.call_count == 1


def test_store_analysis_nonexistent_relationship(knowledge_repository, neo4j_manager):
    """存在しないエンティティへのリレーションシップの保存をテストする。"""
    analysis_result = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "999", "type": "RELATED_TO"}  # 存在しないターゲット
        ],
        "impact_scores": {
            "1": 0.8
        }
    }

    # モックの設定
    neo4j_manager.create_entity_node.return_value = {"id": "1"}
    neo4j_manager.create_relationship.side_effect = Neo4jError("ターゲットが存在しません")

    # テスト実行
    with pytest.raises(DatabaseError):
        knowledge_repository.store_analysis(analysis_result)


def test_store_analysis_empty_data(knowledge_repository):
    """空のデータの保存をテストする。"""
    empty_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    # 空のデータは有効
    knowledge_repository.store_analysis(empty_result)


def test_store_analysis_special_characters(knowledge_repository, neo4j_manager):
    """特殊文字を含むデータの保存をテストする。"""
    analysis_result = {
        "entities": [
            {"id": "1", "name": "特殊文字!@#$%^&*()", "type": "TYPE1"}
        ],
        "relationships": [],
        "impact_scores": {
            "1": 0.8
        }
    }

    # モックの設定
    neo4j_manager.create_entity_node.return_value = {"id": "1"}

    # テスト実行
    knowledge_repository.store_analysis(analysis_result)

    # 検証
    neo4j_manager.create_entity_node.assert_called_once_with(
        entity_id="1",
        entity_type="TYPE1",
        properties={"name": "特殊文字!@#$%^&*()"}
    )


def test_store_analysis_transaction_rollback(knowledge_repository, neo4j_manager):
    """トランザクションのロールバックをテストする。"""
    analysis_result = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        }
    }

    # モックの設定
    neo4j_manager.create_entity_node.side_effect = DatabaseError("データベースエラー")

    # テスト実行
    with pytest.raises(DatabaseError):
        knowledge_repository.store_analysis(analysis_result)

    # ロールバックが呼ばれることを確認
    neo4j_manager.rollback_transaction.assert_called_once()


def test_validate_basic_structure_success(knowledge_repository):
    """基本構造の検証が成功するケースをテストする。"""
    valid_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_basic_structure(valid_result) is None


def test_validate_basic_structure_invalid_type(knowledge_repository):
    """不正な型の基本構造の検証をテストする。"""
    invalid_result = []  # リスト

    with pytest.raises(ValidationError):
        knowledge_repository._validate_basic_structure(invalid_result)


def test_validate_basic_structure_missing_keys(knowledge_repository):
    """必須キーが欠けている基本構造の検証をテストする。"""
    invalid_result = {
        "entities": [],
        # relationshipsが欠けている
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_basic_structure(invalid_result)


def test_validate_field_types_success(knowledge_repository):
    """フィールドの型の検証が成功するケースをテストする。"""
    valid_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {}
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_field_types(valid_result) is None


def test_validate_field_types_invalid_entities(knowledge_repository):
    """不正な型のエンティティフィールドの検証をテストする。"""
    invalid_result = {
        "entities": "invalid",  # 文字列
        "relationships": [],
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_field_types(invalid_result)


def test_validate_field_types_invalid_relationships(knowledge_repository):
    """不正な型のリレーションシップフィールドの検証をテストする。"""
    invalid_result = {
        "entities": [],
        "relationships": "invalid",  # 文字列
        "impact_scores": {}
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_field_types(invalid_result)


def test_validate_field_types_invalid_impact_scores(knowledge_repository):
    """不正な型のインパクトスコアフィールドの検証をテストする。"""
    invalid_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": []  # リスト
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_field_types(invalid_result)


def test_validate_field_types_invalid_source_url(knowledge_repository):
    """不正な型のソースURLフィールドの検証をテストする。"""
    invalid_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {},
        "source_url": 123  # 数値
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_field_types(invalid_result)


def test_validate_field_types_invalid_analyzed_at(knowledge_repository):
    """不正な型の分析日時フィールドの検証をテストする。"""
    invalid_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {},
        "analyzed_at": "invalid"  # 不正な日時形式
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_field_types(invalid_result)


def test_validate_impact_scores_basic_types_success(knowledge_repository):
    """インパクトスコアの基本型の検証が成功するケースをテストする。"""
    valid_scores = {
        "1": 0.8,
        "2": 0.6
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_impact_scores_basic_types(valid_scores) is None


def test_validate_impact_scores_basic_types_invalid_scores(knowledge_repository):
    """不正な型のスコア値の検証をテストする。"""
    invalid_scores = {
        "1": "0.8",  # 文字列
        "2": None    # None
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores_basic_types(invalid_scores)


def test_validate_impact_scores_basic_types_invalid_entities(knowledge_repository):
    """不正な型のエンティティIDの検証をテストする。"""
    invalid_scores = {
        1: 0.8,      # 数値のキー
        None: 0.6    # Noneのキー
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores_basic_types(invalid_scores)


def test_extract_entity_ids_success(knowledge_repository):
    """エンティティIDの抽出が成功するケースをテストする。"""
    entities = [
        {"id": "1", "name": "エンティティ1", "type": "TYPE1"},
        {"id": "2", "name": "エンティティ2", "type": "TYPE2"}
    ]

    ids = knowledge_repository._extract_entity_ids(entities)
    assert ids == {"1", "2"}


def test_extract_entity_ids_empty_list(knowledge_repository):
    """空のエンティティリストからのID抽出をテストする。"""
    ids = knowledge_repository._extract_entity_ids([])
    assert ids == set()


def test_extract_entity_ids_invalid_entities(knowledge_repository):
    """不正なエンティティからのID抽出をテストする。"""
    invalid_entities = [
        {"name": "エンティティ1", "type": "TYPE1"}  # idが欠けている
    ]

    with pytest.raises(ValidationError):
        knowledge_repository._extract_entity_ids(invalid_entities)


def test_validate_impact_scores_consistency_success(knowledge_repository):
    """インパクトスコアの一貫性の検証が成功するケースをテストする。"""
    entities = [
        {"id": "1", "name": "エンティティ1", "type": "TYPE1"},
        {"id": "2", "name": "エンティティ2", "type": "TYPE2"}
    ]
    scores = {
        "1": 0.8,
        "2": 0.6
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_impact_scores_consistency(entities, scores) is None


def test_validate_impact_scores_consistency_missing_scores(knowledge_repository):
    """スコアが欠けているエンティティの検証をテストする。"""
    entities = [
        {"id": "1", "name": "エンティティ1", "type": "TYPE1"},
        {"id": "2", "name": "エンティティ2", "type": "TYPE2"}
    ]
    scores = {
        "1": 0.8
        # "2"のスコアが欠けている
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores_consistency(entities, scores)


def test_validate_impact_scores_consistency_extra_scores(knowledge_repository):
    """余分なスコアを持つエンティティの検証をテストする。"""
    entities = [
        {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
    ]
    scores = {
        "1": 0.8,
        "2": 0.6  # 存在しないエンティティのスコア
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_impact_scores_consistency(entities, scores)


def test_validate_score_values_success(knowledge_repository):
    """スコア値の検証が成功するケースをテストする。"""
    valid_scores = {
        "1": 0.8,
        "2": 0.6
    }

    # 検証が成功することを確認
    assert knowledge_repository._validate_score_values(valid_scores) is None


def test_validate_score_values_invalid_type(knowledge_repository):
    """不正な型のスコア値の検証をテストする。"""
    invalid_scores = {
        "1": "0.8",  # 文字列
        "2": None    # None
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_score_values(invalid_scores)


def test_validate_score_values_out_of_range(knowledge_repository):
    """範囲外のスコア値の検証をテストする。"""
    invalid_scores = {
        "1": 1.5,  # 1.0を超えている
        "2": -0.5  # 0.0未満
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_score_values(invalid_scores)


def test_validate_score_values_special_values(knowledge_repository):
    """特殊な値のスコア値の検証をテストする。"""
    invalid_scores = {
        "1": float('inf'),   # 無限大
        "2": float('nan')    # 非数
    }

    with pytest.raises(ValidationError):
        knowledge_repository._validate_score_values(invalid_scores)


def test_store_analysis_data_success(knowledge_repository, neo4j_manager):
    """分析データの保存が成功するケースをテストする。"""
    analysis_data = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "RELATED_TO"}
        ],
        "impact_scores": {
            "1": 0.8,
            "2": 0.6
        },
        "source_url": "https://example.com",
        "analyzed_at": datetime.now().isoformat()
    }

    # モックの設定
    neo4j_manager.create_entity_node.return_value = {"id": "1"}
    neo4j_manager.create_relationship.return_value = None

    # テスト実行
    knowledge_repository._store_analysis_data(analysis_data)

    # 検証
    neo4j_manager.create_entity_node.assert_called_once()
    neo4j_manager.create_relationship.assert_called_once()


def test_store_analysis_data_entity_error(knowledge_repository, neo4j_manager):
    """エンティティの保存エラーをテストする。"""
    analysis_data = {
        "entities": [
            {"id": "1", "name": "エンティティ1", "type": "TYPE1"}
        ],
        "relationships": [],
        "impact_scores": {
            "1": 0.8
        }
    }

    # モックの設定
    neo4j_manager.create_entity_node.side_effect = DatabaseError("エンティティ作成エラー")

    # テスト実行
    with pytest.raises(DatabaseError):
        knowledge_repository._store_analysis_data(analysis_data)

    # ロールバックが呼ばれることを確認
    neo4j_manager.rollback_transaction.assert_called_once() 