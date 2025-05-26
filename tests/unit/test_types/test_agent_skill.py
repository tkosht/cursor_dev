"""
AgentSkillの包括的単体テスト (TDD実践版)

このテストは TDD (Test Driven Development) アプローチに基づいて作成されています:
- Red: 失敗するテストを先に書く
- Green: テストを通すための最小限の実装
- Refactor: コードを改善する

【テスト対象】
- a2a.types.AgentSkill のバリデーション・作成・操作
"""

import pytest
from pydantic import ValidationError

# a2a-sdk インポート（実機調査で確認済みの正しいAPI）
try:
    from a2a.types import AgentSkill
except ImportError:
    pytest.skip("a2a-sdk not available", allow_module_level=True)


@pytest.mark.unit
class TestAgentSkillCreation:
    """AgentSkill作成のTDDテスト"""
    
    def test_create_with_all_required_fields(self, valid_agent_skill_data):
        """正常ケース: 全必須フィールド指定での作成"""
        # Given: 有効な必須フィールドデータ
        skill_data = valid_agent_skill_data
        
        # When: AgentSkillを作成
        skill = AgentSkill(**skill_data)
        
        # Then: 期待される値で正確に作成される
        assert skill.id == skill_data["id"]
        assert skill.name == skill_data["name"]
        assert skill.description == skill_data["description"]
        assert skill.tags == skill_data["tags"]
        assert isinstance(skill.tags, list)
        assert len(skill.tags) == len(skill_data["tags"])
    
    def test_create_missing_id_field_raises_validation_error(self):
        """異常ケース: id フィールド不足でValidationError"""
        # Given: id フィールドが不足したデータ
        skill_data = {
            "name": "Test Skill",
            "description": "A test skill without id",
            "tags": ["test"]
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError) as exc_info:
            AgentSkill(**skill_data)
        
        # Then: エラーメッセージに「id」「Field required」が含まれる
        error_str = str(exc_info.value)
        assert "id" in error_str
        assert "Field required" in error_str or "missing" in error_str.lower()
    
    def test_create_missing_name_field_raises_validation_error(self):
        """異常ケース: name フィールド不足でValidationError"""
        # Given: name フィールドが不足したデータ
        skill_data = {
            "id": "test_skill",
            "description": "A test skill without name",
            "tags": ["test"]
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError) as exc_info:
            AgentSkill(**skill_data)
        
        # Then: エラーメッセージに「name」が含まれる
        error_str = str(exc_info.value)
        assert "name" in error_str
    
    def test_create_missing_description_field_raises_validation_error(self):
        """異常ケース: description フィールド不足でValidationError"""
        # Given: description フィールドが不足したデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill",
            "tags": ["test"]
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError) as exc_info:
            AgentSkill(**skill_data)
        
        # Then: エラーメッセージに「description」が含まれる
        error_str = str(exc_info.value)
        assert "description" in error_str
    
    def test_create_missing_tags_field_raises_validation_error(self):
        """異常ケース: tags フィールド不足でValidationError"""
        # Given: tags フィールドが不足したデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill",
            "description": "A test skill without tags"
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError) as exc_info:
            AgentSkill(**skill_data)
        
        # Then: エラーメッセージに「tags」が含まれる
        error_str = str(exc_info.value)
        assert "tags" in error_str


@pytest.mark.unit
class TestAgentSkillValidation:
    """AgentSkillのバリデーションテスト"""
    
    @pytest.mark.parametrize("invalid_id", [
        None,           # None値
        "",             # 空文字
        123,            # 数値
        [],             # リスト
        {},             # 辞書
        True,           # ブール値
    ])
    def test_create_with_invalid_id_types_raises_validation_error(self, invalid_id):
        """パラメータ化テスト: 無効なidの型でValidationError"""
        # Given: 無効なid型を含むデータ
        skill_data = {
            "id": invalid_id,
            "name": "Test Skill",
            "description": "Test skill with invalid id",
            "tags": ["test"]
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError):
            AgentSkill(**skill_data)
    
    @pytest.mark.parametrize("invalid_tags", [
        None,           # None値
        "string",       # 文字列（リストでない）
        123,            # 数値
        {},             # 辞書
        True,           # ブール値
    ])
    def test_create_with_invalid_tags_types_raises_validation_error(self, invalid_tags):
        """パラメータ化テスト: 無効なtagsの型でValidationError"""
        # Given: 無効なtags型を含むデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill", 
            "description": "Test skill with invalid tags",
            "tags": invalid_tags
        }
        
        # When/Then: ValidationErrorが発生する
        with pytest.raises(ValidationError):
            AgentSkill(**skill_data)
    
    def test_create_with_empty_tags_list(self):
        """境界値ケース: 空のtagsリスト"""
        # Given: 空のtagsリストを含むデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill",
            "description": "Test skill with empty tags",
            "tags": []
        }
        
        # When: AgentSkillを作成
        skill = AgentSkill(**skill_data)
        
        # Then: 正常に作成され、空のリストが設定される
        assert skill.tags == []
        assert isinstance(skill.tags, list)
        assert len(skill.tags) == 0
    
    def test_create_with_single_tag(self):
        """境界値ケース: 単一のtag"""
        # Given: 単一のtagを含むデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill",
            "description": "Test skill with single tag",
            "tags": ["single"]
        }
        
        # When: AgentSkillを作成
        skill = AgentSkill(**skill_data)
        
        # Then: 正常に作成され、単一tagが設定される
        assert skill.tags == ["single"]
        assert len(skill.tags) == 1


@pytest.mark.unit
class TestAgentSkillEquality:
    """AgentSkillの等価性テスト"""
    
    def test_two_identical_skills_are_equal(self):
        """同一データから作成したAgentSkillは等価"""
        # Given: 同一のスキルデータ
        skill_data = {
            "id": "test_skill",
            "name": "Test Skill",
            "description": "Test skill for equality",
            "tags": ["test", "equality"]
        }
        
        # When: 2つのAgentSkillを作成
        skill1 = AgentSkill(**skill_data)
        skill2 = AgentSkill(**skill_data)
        
        # Then: 等価である
        assert skill1 == skill2
        assert skill1.id == skill2.id
        assert skill1.name == skill2.name
        assert skill1.description == skill2.description
        assert skill1.tags == skill2.tags
    
    def test_skills_with_different_ids_are_not_equal(self):
        """異なるidを持つAgentSkillは非等価"""
        # Given: idが異なるスキルデータ
        skill1 = AgentSkill(
            id="skill1",
            name="Test Skill",
            description="Test skill",
            tags=["test"]
        )
        skill2 = AgentSkill(
            id="skill2",
            name="Test Skill",
            description="Test skill",
            tags=["test"]
        )
        
        # When/Then: 非等価である
        assert skill1 != skill2
        assert skill1.id != skill2.id


@pytest.mark.unit
class TestAgentSkillStringRepresentation:
    """AgentSkillの文字列表現テスト"""
    
    def test_skill_string_representation_contains_key_info(self):
        """AgentSkillの文字列表現に重要な情報が含まれる"""
        # Given: スキルデータ
        skill = AgentSkill(
            id="test_skill",
            name="Test Skill",
            description="Test skill for string representation",
            tags=["test", "string"]
        )
        
        # When: 文字列表現を取得
        skill_str = str(skill)
        
        # Then: 重要な情報が含まれる
        assert "test_skill" in skill_str or "Test Skill" in skill_str
        # 実装依存のため、idかnameのどちらかが含まれていればOK 