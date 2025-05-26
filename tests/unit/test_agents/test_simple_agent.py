"""
SimpleTestAgentの包括的単体テスト (TDD実践版)

このテストは TDD (Test Driven Development) アプローチに基づいて作成されています:
- Red: 失敗するテストを先に書く
- Green: テストを通すための最小限の実装
- Refactor: コードを改善する

【テスト対象】
- app.a2a_prototype.agents.simple_agent.SimpleTestAgent
- Given-When-Then パターンと AAA (Arrange-Act-Assert) パターンを活用
"""

import pytest

from app.a2a_prototype.agents.simple_agent import (
    SimpleTestAgent,
    create_test_agent,
)

# a2a-sdk インポート（テスト用）
try:
    from a2a.types import AgentSkill
except ImportError:
    pytest.skip("a2a-sdk not available", allow_module_level=True)


@pytest.mark.unit
class TestSimpleTestAgentCreation:
    """SimpleTestAgent作成のTDDテスト"""

    def test_create_agent_with_valid_config(self, sample_agent_config):
        """正常ケース: 有効な設定でのエージェント作成"""
        # Given: 有効なAgentConfig
        config = sample_agent_config

        # When: SimpleTestAgentを作成
        agent = SimpleTestAgent(config)

        # Then: 正常に作成され、設定が保持される
        assert agent.config == config
        assert agent.config.name == "test-agent"
        assert agent.config.url == "http://localhost:8001"
        assert agent.config.port == 8001

    def test_create_test_agent_helper_function(self):
        """create_test_agent ヘルパー関数のテスト"""
        # Given: ポート番号
        port = 8002

        # When: create_test_agentを呼び出し
        agent = create_test_agent(port)

        # Then: 期待される設定でエージェントが作成される
        assert isinstance(agent, SimpleTestAgent)
        assert agent.config.name == "simple-test-agent"
        assert agent.config.port == port
        assert agent.config.url == f"http://localhost:{port}"


@pytest.mark.unit
class TestSimpleTestAgentSkills:
    """SimpleTestAgentのスキル機能テスト"""

    def test_get_skills_returns_expected_skills(self, sample_agent_config):
        """get_skills: 期待されるスキル一覧を返す"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: スキル一覧を取得
        skills = agent.get_skills()

        # Then: 期待されるスキルが含まれる
        assert isinstance(skills, list)
        assert len(skills) == 2

        skill_ids = [skill.id for skill in skills]
        assert "echo" in skill_ids
        assert "greet" in skill_ids

        # スキルの詳細確認
        echo_skill = next(skill for skill in skills if skill.id == "echo")
        assert echo_skill.name == "echo"
        assert "Echo back" in echo_skill.description
        assert "text" in echo_skill.tags
        assert "utility" in echo_skill.tags

    def test_get_skills_returns_agent_skill_objects(self, sample_agent_config):
        """get_skills: AgentSkillオブジェクトを返す"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: スキル一覧を取得
        skills = agent.get_skills()

        # Then: 全てのスキルがAgentSkillオブジェクト
        for skill in skills:
            assert isinstance(skill, AgentSkill)
            assert hasattr(skill, "id")
            assert hasattr(skill, "name")
            assert hasattr(skill, "description")
            assert hasattr(skill, "tags")


@pytest.mark.unit
class TestSimpleTestAgentUserInputProcessing:
    """SimpleTestAgentのユーザー入力処理テスト"""

    @pytest.mark.asyncio
    async def test_process_user_input_hello_command(self, sample_agent_config):
        """process_user_input: helloコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: helloコマンドを実行
        result = await agent.process_user_input("hello")

        # Then: 適切な挨拶が返される
        assert "Hello!" in result
        assert agent.config.name in result
        assert "How can I help you today?" in result

    @pytest.mark.asyncio
    async def test_process_user_input_hi_command(self, sample_agent_config):
        """process_user_input: hiコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: hiコマンドを実行
        result = await agent.process_user_input("hi")

        # Then: 適切な挨拶が返される
        assert "Hello!" in result
        assert agent.config.name in result

    @pytest.mark.asyncio
    async def test_process_user_input_echo_command_with_message(
        self, sample_agent_config
    ):
        """process_user_input: echoコマンドでメッセージ付き"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        test_message = "Test Message"

        # When: echoコマンドを実行
        result = await agent.process_user_input(f"echo {test_message}")

        # Then: メッセージがエコーされる
        assert result == f"Echo: {test_message}"
        assert "Echo:" in result
        assert test_message in result

    @pytest.mark.asyncio
    async def test_process_user_input_echo_command_without_message(
        self, sample_agent_config
    ):
        """process_user_input: echoコマンドでメッセージなし"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: メッセージなしのechoコマンドを実行
        result = await agent.process_user_input("echo")

        # Then: 空メッセージの通知
        assert result == "Echo: (empty message)"
        assert "empty message" in result

    @pytest.mark.asyncio
    async def test_process_user_input_echo_command_with_only_spaces(
        self, sample_agent_config
    ):
        """process_user_input: echoコマンドでスペースのみ"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: スペースのみのechoコマンドを実行
        result = await agent.process_user_input("echo   ")

        # Then: 空メッセージとして処理される
        assert result == "Echo: (empty message)"

    @pytest.mark.asyncio
    async def test_process_user_input_status_command(
        self, sample_agent_config
    ):
        """process_user_input: statusコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: statusコマンドを実行
        result = await agent.process_user_input("status")

        # Then: ステータス情報が返される
        assert agent.config.name in result
        assert agent.config.url in result
        assert "Status: OK" in result

    @pytest.mark.asyncio
    async def test_process_user_input_help_command(self, sample_agent_config):
        """process_user_input: helpコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: helpコマンドを実行
        result = await agent.process_user_input("help")

        # Then: ヘルプメッセージが返される
        assert "Available commands" in result
        assert agent.config.name in result
        assert "hello/hi" in result
        assert "echo" in result
        assert "status" in result
        assert "help" in result

    @pytest.mark.asyncio
    async def test_process_user_input_question_mark_help(
        self, sample_agent_config
    ):
        """process_user_input: ?でのヘルプ表示"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: ?を実行
        result = await agent.process_user_input("?")

        # Then: ヘルプメッセージが返される
        assert "Available commands" in result

    @pytest.mark.asyncio
    async def test_process_user_input_unknown_command(
        self, sample_agent_config
    ):
        """process_user_input: 未知のコマンドの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        unknown_input = "unknown command"

        # When: 未知のコマンドを実行
        result = await agent.process_user_input(unknown_input)

        # Then: 適切なフォールバックメッセージ
        assert f"I received: '{unknown_input}'" in result
        assert "Try 'help'" in result

    @pytest.mark.parametrize(
        "input_text,expected_command",
        [
            ("HELLO", "hello"),  # 大文字
            ("Hello", "hello"),  # キャピタライズ
            ("  hello  ", "hello"),  # 前後スペース
            ("ECHO test", "echo"),  # 大文字echo
            ("  STATUS  ", "status"),  # 前後スペース付きstatus
        ],
    )
    @pytest.mark.asyncio
    async def test_process_user_input_case_insensitive_and_whitespace_handling(
        self, sample_agent_config, input_text, expected_command
    ):
        """パラメータ化テスト: 大文字小文字・空白の処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: 各種入力を実行
        result = await agent.process_user_input(input_text)

        # Then: 適切に処理される（コマンドが認識される）
        if expected_command == "hello":
            assert "Hello!" in result
        elif expected_command == "echo":
            assert "Echo:" in result
        elif expected_command == "status":
            assert "Status: OK" in result


@pytest.mark.unit
class TestSimpleTestAgentConfiguration:
    """SimpleTestAgentの設定関連テスト"""

    def test_agent_config_is_preserved(self, sample_agent_config):
        """エージェント設定が正しく保持される"""
        # Given: AgentConfig
        config = sample_agent_config

        # When: SimpleTestAgentを作成
        agent = SimpleTestAgent(config)

        # Then: 設定が正確に保持される
        assert agent.config is config
        assert agent.config.name == config.name
        assert agent.config.description == config.description
        assert agent.config.url == config.url
        assert agent.config.port == config.port

    def test_agent_config_modification_affects_agent(
        self, sample_agent_config
    ):
        """設定の変更がエージェントに反映される"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        original_name = agent.config.name

        # When: 設定を変更
        new_name = "modified-agent"
        agent.config.name = new_name

        # Then: 変更が反映される
        assert agent.config.name == new_name
        assert agent.config.name != original_name


@pytest.mark.unit
class TestSimpleTestAgentEdgeCases:
    """SimpleTestAgentのエッジケーステスト"""

    @pytest.mark.asyncio
    async def test_process_user_input_empty_string(self, sample_agent_config):
        """process_user_input: 空文字列の処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: 空文字列を実行
        result = await agent.process_user_input("")

        # Then: 適切に処理される
        assert "I received: ''" in result
        assert "Try 'help'" in result

    @pytest.mark.asyncio
    async def test_process_user_input_only_whitespace(
        self, sample_agent_config
    ):
        """process_user_input: 空白のみの処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)

        # When: 空白のみを実行
        result = await agent.process_user_input("   ")

        # Then: 適切に処理される（空白は除去される）
        assert "I received: ''" in result or "I received: '   '" in result
        assert "Try 'help'" in result

    @pytest.mark.asyncio
    async def test_process_user_input_very_long_input(
        self, sample_agent_config
    ):
        """process_user_input: 非常に長い入力の処理"""
        # Given: SimpleTestAgent
        agent = SimpleTestAgent(sample_agent_config)
        long_input = "echo " + "a" * 1000  # 1000文字のメッセージ

        # When: 長いechoコマンドを実行
        result = await agent.process_user_input(long_input)

        # Then: 正常に処理される
        assert "Echo:" in result
        assert "a" * 1000 in result
        assert len(result) > 1000


@pytest.mark.unit
class TestSimpleTestAgentIntegrationWithBaseClass:
    """SimpleTestAgentと基底クラスの統合テスト"""

    def test_simple_agent_inherits_from_base_agent(self, sample_agent_config):
        """SimpleTestAgentが適切にBaseA2AAgentを継承"""
        # Given/When: SimpleTestAgentを作成
        agent = SimpleTestAgent(sample_agent_config)

        # Then: BaseA2AAgentのメソッドが利用可能
        assert hasattr(agent, "get_skills")
        assert hasattr(agent, "process_user_input")
        assert hasattr(agent, "config")

        # get_skillsメソッドが呼び出し可能
        skills = agent.get_skills()
        assert isinstance(skills, list)
