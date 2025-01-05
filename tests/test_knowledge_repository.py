from datetime import datetime
import pytest
from unittest.mock import Mock, patch

from app.knowledge_repository import KnowledgeRepository


@pytest.fixture
def neo4j_manager_mock():
    return Mock()


@pytest.fixture
def repository(neo4j_manager_mock):
    return KnowledgeRepository(neo4j_manager_mock)


@pytest.fixture
def valid_analysis_result():
    return {
        'entities': [
            {
                'id': 'company1',
                'type': 'Company',
                'name': 'テスト株式会社',
                'description': 'テスト企業の説明'
            }
        ],
        'relationships': [
            {
                'source_id': 'company1',
                'target_id': 'product1',
                'type': 'PRODUCES',
                'strength': 0.8,
                'description': '主力製品'
            }
        ],
        'impact_scores': {
            'company1': 0.75
        },
        'source_url': 'https://example.com/news/1',
        'analyzed_at': datetime.now()
    }


def test_store_analysis_success(repository, neo4j_manager_mock, valid_analysis_result):
    """store_analysis()の正常系テスト"""
    # _check_duplicateがFalseを返すようにモック設定
    neo4j_manager_mock.run_query.return_value = [{'count': 0}]

    # 実行
    repository.store_analysis(valid_analysis_result)

    # create_nodeが正しく呼ばれたことを確認
    neo4j_manager_mock.create_node.assert_called_once()
    call_args = neo4j_manager_mock.create_node.call_args[1]
    assert call_args['labels'] == ['Company']
    assert call_args['properties']['id'] == 'company1'
    assert call_args['properties']['name'] == 'テスト株式会社'

    # create_relationshipが正しく呼ばれたことを確認
    neo4j_manager_mock.create_relationship.assert_called_once()
    call_args = neo4j_manager_mock.create_relationship.call_args[1]
    assert call_args['start_node_id'] == 'company1'
    assert call_args['end_node_id'] == 'product1'
    assert call_args['relationship_type'] == 'PRODUCES'
    assert call_args['properties']['strength'] == 0.8

    # update_nodeが正しく呼ばれたことを確認
    neo4j_manager_mock.update_node.assert_called_once_with(
        node_id='company1',
        properties={'impact_score': 0.75}
    )


def test_store_analysis_duplicate_entity(repository, neo4j_manager_mock, valid_analysis_result):
    """既存エンティティの更新テスト"""
    # _check_duplicateがTrueを返すようにモック設定
    neo4j_manager_mock.run_query.return_value = [{'count': 1}]

    # 実行
    repository.store_analysis(valid_analysis_result)

    # create_nodeが呼ばれていないことを確認
    neo4j_manager_mock.create_node.assert_not_called()

    # update_nodeが2回呼ばれたことを確認（タイムスタンプ更新と影響度スコア更新）
    assert neo4j_manager_mock.update_node.call_count == 2


def test_store_analysis_invalid_format(repository):
    """不正な形式の分析結果を渡した場合のテスト"""
    invalid_result = {
        'entities': [],  # 必須キーが不足
        'relationships': []
    }

    with pytest.raises(ValueError) as exc_info:
        repository.store_analysis(invalid_result)
    assert "Invalid analysis result format" in str(exc_info.value)


def test_store_analysis_database_error(repository, neo4j_manager_mock, valid_analysis_result):
    """データベース操作エラー時のテスト"""
    neo4j_manager_mock.create_node.side_effect = Exception("Database connection failed")

    with pytest.raises(RuntimeError) as exc_info:
        repository.store_analysis(valid_analysis_result)
    assert "Failed to store analysis result" in str(exc_info.value)


def test_validate_analysis_result_success(repository, valid_analysis_result):
    """_validate_analysis_result()の正常系テスト"""
    assert repository._validate_analysis_result(valid_analysis_result) is True


def test_validate_analysis_result_missing_required_keys(repository):
    """必須キーが欠落している場合のテスト"""
    invalid_result = {
        'entities': [],
        'relationships': []  # impact_scores, source_url, analyzed_atが欠落
    }
    assert repository._validate_analysis_result(invalid_result) is False


def test_validate_analysis_result_invalid_entity(repository, valid_analysis_result):
    """不正なエンティティ形式のテスト"""
    invalid_result = valid_analysis_result.copy()
    invalid_result['entities'] = [{'id': 'test'}]  # type, nameが欠落
    assert repository._validate_analysis_result(invalid_result) is False


def test_validate_analysis_result_invalid_relationship(repository, valid_analysis_result):
    """不正な関係性形式のテスト"""
    invalid_result = valid_analysis_result.copy()
    invalid_result['relationships'] = [{'source_id': 'test'}]  # target_id, typeが欠落
    assert repository._validate_analysis_result(invalid_result) is False


def test_check_duplicate_exists(repository, neo4j_manager_mock):
    """_check_duplicate()で既存ノードを検出するテスト"""
    neo4j_manager_mock.run_query.return_value = [{'count': 1}]
    assert repository._check_duplicate('test_id', 'TestLabel') is True


def test_check_duplicate_not_exists(repository, neo4j_manager_mock):
    """_check_duplicate()で未存在ノードを検出するテスト"""
    neo4j_manager_mock.run_query.return_value = [{'count': 0}]
    assert repository._check_duplicate('test_id', 'TestLabel') is False


def test_update_timestamp(repository, neo4j_manager_mock):
    """_update_timestamp()の動作テスト"""
    repository._update_timestamp('test_id', 'TestLabel')
    
    neo4j_manager_mock.update_node.assert_called_once()
    call_args = neo4j_manager_mock.update_node.call_args[1]
    assert call_args['node_id'] == 'test_id'
    assert 'updated_at' in call_args['properties'] 