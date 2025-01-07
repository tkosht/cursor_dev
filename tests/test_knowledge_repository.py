"""KnowledgeRepositoryのテストモジュール。"""

import os
from datetime import datetime

import pytest

from app.knowledge_repository import KnowledgeRepository
from app.neo4j_manager import Neo4jManager


@pytest.fixture(autouse=True)
def setup_test_env():
    """テスト環境のセットアップ"""
    # 現在の環境変数を保存
    original_env = {
        'NEO4J_URI': os.getenv('NEO4J_URI'),
        'neo4j_user': os.getenv('neo4j_user'),
        'neo4j_pswd': os.getenv('neo4j_pswd')
    }

    # .env.test から環境変数を読み込む
    with open('.env.test') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    yield

    # テスト後に元の環境変数を復元
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)


@pytest.fixture
def neo4j_manager():
    """Neo4jManagerのフィクスチャ"""
    return Neo4jManager()


@pytest.fixture
def knowledge_repo(neo4j_manager):
    """KnowledgeRepositoryのフィクスチャ"""
    return KnowledgeRepository(neo4j_manager)


@pytest.fixture
def valid_analysis_result():
    """有効な分析結果のフィクスチャ"""
    return {
        "entities": [
            {
                "id": "company_1",
                "name": "テスト株式会社",
                "type": "Company",
                "description": "テスト企業の説明"
            },
            {
                "id": "product_1",
                "name": "テスト製品",
                "type": "Product",
                "description": "テスト製品の説明"
            }
        ],
        "relationships": [
            {
                "source": "テスト株式会社",
                "target": "テスト製品",
                "type": "PRODUCES",
                "description": "製品の製造",
                "strength": 0.8
            }
        ],
        "impact_scores": {
            "company_1": 0.7,
            "product_1": 0.5
        },
        "source_url": "https://example.com/test",
        "analyzed_at": datetime.now()
    }


def test_init(knowledge_repo):
    """初期化のテスト"""
    assert knowledge_repo is not None
    assert isinstance(knowledge_repo.neo4j_manager, Neo4jManager)


def test_store_analysis_success(knowledge_repo, valid_analysis_result):
    """分析結果の保存成功テスト"""
    result = knowledge_repo.store_analysis(valid_analysis_result)
    assert result is True


def test_store_analysis_invalid_format(knowledge_repo):
    """不正な形式の分析結果に対するテスト"""
    invalid_result = {
        "entities": [],  # 空のエンティティリスト
        "relationships": []  # 空の関係性リスト
    }
    with pytest.raises(ValueError):
        knowledge_repo.store_analysis(invalid_result)


def test_validate_analysis_result_success(knowledge_repo, valid_analysis_result):
    """分析結果の検証成功テスト"""
    assert knowledge_repo._validate_analysis_result(valid_analysis_result) is True


def test_validate_analysis_result_missing_keys(knowledge_repo):
    """必須キーが欠けている分析結果の検証テスト"""
    invalid_result = {
        "entities": [],
        "relationships": []
    }
    assert knowledge_repo._validate_analysis_result(invalid_result) is False


def test_validate_entities_success(knowledge_repo, valid_analysis_result):
    """エンティティ検証成功テスト"""
    assert knowledge_repo._validate_entities(valid_analysis_result["entities"]) is True


def test_validate_entities_invalid_format(knowledge_repo):
    """不正な形式のエンティティに対するテスト"""
    invalid_entities = [
        {
            "name": "テスト"  # idとtypeが欠けている
        }
    ]
    assert knowledge_repo._validate_entities(invalid_entities) is False


def test_validate_relationships_success(knowledge_repo, valid_analysis_result):
    """関係性検証成功テスト"""
    assert knowledge_repo._validate_relationships(valid_analysis_result["relationships"]) is True


def test_validate_relationships_invalid_format(knowledge_repo):
    """不正な形式の関係性に対するテスト"""
    invalid_relationships = [
        {
            "source": "テスト1"  # targetとtypeが欠けている
        }
    ]
    assert knowledge_repo._validate_relationships(invalid_relationships) is False


def test_validate_impact_scores_success(knowledge_repo, valid_analysis_result):
    """影響度スコア検証成功テスト"""
    assert knowledge_repo._validate_impact_scores(
        valid_analysis_result["impact_scores"],
        valid_analysis_result["entities"]
    ) is True


def test_validate_impact_scores_invalid_range(knowledge_repo):
    """範囲外の影響度スコアに対するテスト"""
    entities = [{"id": "entity1", "name": "テスト", "type": "Test"}]
    invalid_scores = {
        "entity1": 1.5  # 1.0を超える不正な値
    }
    assert knowledge_repo._validate_impact_scores(invalid_scores, entities) is False


def test_validate_impact_scores_boundary(knowledge_repo):
    """影響度スコアの境界値テスト"""
    entities = [
        {"id": "entity1", "name": "テスト1", "type": "Test"},
        {"id": "entity2", "name": "テスト2", "type": "Test"},
        {"id": "entity3", "name": "テスト3", "type": "Test"}
    ]
    boundary_scores = {
        "entity1": 0.0,  # 最小値
        "entity2": 1.0,  # 最大値
        "entity3": 0.5   # 中間値
    }
    assert knowledge_repo._validate_impact_scores(boundary_scores, entities) is True


def test_validate_impact_scores_invalid_type(knowledge_repo):
    """不正な型の影響度スコアに対するテスト"""
    entities = [{"id": "entity1", "name": "テスト", "type": "Test"}]
    invalid_scores = {
        "entity1": "invalid"  # 数値ではない
    }
    assert knowledge_repo._validate_impact_scores(invalid_scores, entities) is False


def test_validate_impact_scores_invalid_dict_type(knowledge_repo):
    """impact_scoresが辞書でない場合のテスト"""
    entities = [{"id": "entity1", "name": "テスト", "type": "Test"}]
    invalid_scores = "not a dict"
    assert knowledge_repo._validate_impact_scores(invalid_scores, entities) is False


def test_validate_impact_scores_invalid_id(knowledge_repo):
    """存在しないエンティティIDのスコアテスト"""
    entities = [{"id": "entity1", "name": "テスト", "type": "Test"}]
    invalid_scores = {
        "nonexistent_id": 0.5
    }
    assert knowledge_repo._validate_impact_scores(invalid_scores, entities) is False


def test_store_entities_success(knowledge_repo, valid_analysis_result):
    """エンティティ保存成功テスト"""
    entity_id_map = knowledge_repo._store_entities(valid_analysis_result)
    assert isinstance(entity_id_map, dict)
    assert len(entity_id_map) == 2
    assert "テスト株式会社" in entity_id_map
    assert "テスト製品" in entity_id_map


def test_store_relationships_success(knowledge_repo, valid_analysis_result):
    """関係性保存成功テスト"""
    entity_id_map = knowledge_repo._store_entities(valid_analysis_result)
    knowledge_repo._store_relationships(valid_analysis_result, entity_id_map)
    # 例外が発生しなければ成功


def test_store_analysis_duplicate_entities(knowledge_repo, valid_analysis_result):
    """重複エンティティの処理テスト"""
    # 同じIDを持つエンティティを追加
    duplicate_entity = {
        "id": "company_1",
        "name": "重複企業",
        "type": "Company",
        "description": "重複企業の説明"
    }
    valid_analysis_result["entities"].append(duplicate_entity)
    result = knowledge_repo.store_analysis(valid_analysis_result)
    assert result is True


def test_store_analysis_nonexistent_relationship(knowledge_repo, valid_analysis_result):
    """存在しないエンティティ間のリレーションシップ作成テスト"""
    invalid_relationship = {
        "source": "存在しない企業",
        "target": "存在しない製品",
        "type": "PRODUCES",
        "description": "無効な関係",
        "strength": 0.8
    }
    valid_analysis_result["relationships"].append(invalid_relationship)
    result = knowledge_repo.store_analysis(valid_analysis_result)
    assert result is True


def test_store_analysis_empty_data(knowledge_repo):
    """空のデータセットのテスト"""
    empty_result = {
        "entities": [],
        "relationships": [],
        "impact_scores": {},
        "source_url": "https://example.com/empty",
        "analyzed_at": datetime.now()
    }
    result = knowledge_repo.store_analysis(empty_result)
    assert result is True


def test_store_analysis_special_characters(knowledge_repo):
    """特殊文字を含むデータのテスト"""
    special_chars_result = {
        "entities": [
            {
                "id": "company_1",
                "name": "テスト株式会社 & Co.",
                "type": "Company",
                "description": "特殊文字テスト: @#$%^&*()"
            }
        ],
        "relationships": [],
        "impact_scores": {"company_1": 0.5},
        "source_url": "https://example.com/test",
        "analyzed_at": datetime.now()
    }
    result = knowledge_repo.store_analysis(special_chars_result)
    assert result is True


def test_store_analysis_transaction_rollback(knowledge_repo, valid_analysis_result, mocker):
    """トランザクションのロールバックテスト"""
    # Neo4jManagerのfind_nodeメソッドが例外を発生させるようにモック
    mocker.patch.object(
        knowledge_repo.neo4j_manager,
        'find_node',
        side_effect=Exception("Database error")
    )
    
    with pytest.raises(Exception):
        knowledge_repo.store_analysis(valid_analysis_result) 