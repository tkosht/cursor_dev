"""
AgentConfigとAgentPresetsの包括的単体テスト (TDD実践版 - カバレッジ90%達成)

未カバー部分の網羅的テスト：
- __post_init__のバリデーション（各種エラーケース）
- AgentPresetsの各プリセットメソッド
- エラーハンドリング分岐の網羅
"""

import pytest

from app.a2a_prototype.utils.config import AgentConfig, AgentPresets


@pytest.mark.unit
class TestAgentConfigValidation:
    """AgentConfigバリデーションテスト（未カバー部分対象）"""

    def test_create_with_valid_data(self):
        """正常ケース: 有効なデータでの作成"""
        # Given: 有効な設定データ
        config = AgentConfig(
            name="test-agent",
            description="Test agent description",
            url="http://localhost:8001",
            port=8001,
        )

        # Then: 正常に作成される
        assert config.name == "test-agent"
        assert config.description == "Test agent description"
        assert config.url == "http://localhost:8001"
        assert config.port == 8001
        assert config.version == "1.0.0"  # デフォルト値

    def test_post_init_validation_empty_name_raises_error(self):
        """異常ケース: 空のname（未カバー行25対象）"""
        # Given/When/Then: 空のnameでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="",  # 空文字
                description="Test description",
                url="http://localhost:8001",
                port=8001,
            )

        assert "Agent name is required" in str(exc_info.value)

    def test_post_init_validation_none_name_raises_error(self):
        """異常ケース: NoneのnameでValueError"""
        # Given/When/Then: NoneのnameでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name=None,  # None値
                description="Test description",
                url="http://localhost:8001",
                port=8001,
            )

        assert "Agent name is required" in str(exc_info.value)

    def test_post_init_validation_empty_description_raises_error(self):
        """異常ケース: 空のdescription（未カバー行27対象）"""
        # Given/When/Then: 空のdescriptionでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="test-agent",
                description="",  # 空文字
                url="http://localhost:8001",
                port=8001,
            )

        assert "Agent description is required" in str(exc_info.value)

    def test_post_init_validation_empty_url_raises_error(self):
        """異常ケース: 空のURL（未カバー行29対象）"""
        # Given/When/Then: 空のURLでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="test-agent",
                description="Test description",
                url="",  # 空文字
                port=8001,
            )

        assert "Agent URL is required" in str(exc_info.value)

    def test_post_init_validation_invalid_port_zero_raises_error(self):
        """異常ケース: ポート0（未カバー行31対象）"""
        # Given/When/Then: ポート0でValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="test-agent",
                description="Test description",
                url="http://localhost:8001",
                port=0,  # 無効なポート
            )

        assert "Port must be a positive integer" in str(exc_info.value)

    def test_post_init_validation_invalid_port_negative_raises_error(self):
        """異常ケース: 負のポート（未カバー行31対象）"""
        # Given/When/Then: 負のポートでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="test-agent",
                description="Test description",
                url="http://localhost:8001",
                port=-1,  # 負のポート
            )

        assert "Port must be a positive integer" in str(exc_info.value)

    def test_post_init_validation_invalid_port_string_raises_error(self):
        """異常ケース: 文字列ポート（未カバー行31対象）"""
        # Given/When/Then: 文字列ポートでValidationError
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                name="test-agent",
                description="Test description",
                url="http://localhost:8001",
                port="8001",  # 文字列（intでない）
            )

        assert "Port must be a positive integer" in str(exc_info.value)


@pytest.mark.unit
class TestAgentPresets:
    """AgentPresetsクラステスト（未カバー部分対象）"""

    def test_weather_agent_preset_default_port(self):
        """weather_agentプリセット: デフォルトポート（未カバー行41対象）"""
        # Given/When: weather_agentプリセットを作成
        config = AgentPresets.weather_agent()

        # Then: 正しい設定で作成される
        assert config.name == "weather-agent"
        assert (
            config.description
            == "Provides current weather information and forecasts"
        )
        assert config.url == "http://localhost:8001"
        assert config.port == 8001
        assert config.version == "1.0.0"

    def test_weather_agent_preset_custom_port(self):
        """weather_agentプリセット: カスタムポート"""
        # Given: カスタムポート
        custom_port = 9001

        # When: weather_agentプリセットをカスタムポートで作成
        config = AgentPresets.weather_agent(port=custom_port)

        # Then: カスタムポートが設定される
        assert config.port == custom_port
        assert config.url == f"http://localhost:{custom_port}"

    def test_chat_agent_preset_default_port(self):
        """chat_agentプリセット: デフォルトポート（未カバー行51対象）"""
        # Given/When: chat_agentプリセットを作成
        config = AgentPresets.chat_agent()

        # Then: 正しい設定で作成される
        assert config.name == "chat-agent"
        assert config.description == "Simple conversational AI agent"
        assert config.url == "http://localhost:8002"
        assert config.port == 8002
        assert config.version == "1.0.0"

    def test_chat_agent_preset_custom_port(self):
        """chat_agentプリセット: カスタムポート"""
        # Given: カスタムポート
        custom_port = 9002

        # When: chat_agentプリセットをカスタムポートで作成
        config = AgentPresets.chat_agent(port=custom_port)

        # Then: カスタムポートが設定される
        assert config.port == custom_port
        assert config.url == f"http://localhost:{custom_port}"

    def test_calculator_agent_preset_default_port(self):
        """calculator_agentプリセット: デフォルトポート（未カバー行61対象）"""
        # Given/When: calculator_agentプリセットを作成
        config = AgentPresets.calculator_agent()

        # Then: 正しい設定で作成される
        assert config.name == "calculator-agent"
        assert config.description == "Performs mathematical calculations"
        assert config.url == "http://localhost:8003"
        assert config.port == 8003
        assert config.version == "1.0.0"

    def test_calculator_agent_preset_custom_port(self):
        """calculator_agentプリセット: カスタムポート"""
        # Given: カスタムポート
        custom_port = 9003

        # When: calculator_agentプリセットをカスタムポートで作成
        config = AgentPresets.calculator_agent(port=custom_port)

        # Then: カスタムポートが設定される
        assert config.port == custom_port
        assert config.url == f"http://localhost:{custom_port}"


@pytest.mark.unit
class TestAgentConfigEdgeCases:
    """AgentConfigエッジケーステスト"""

    def test_custom_version_setting(self):
        """カスタムバージョンの設定"""
        # Given/When: カスタムバージョンで作成
        config = AgentConfig(
            name="test-agent",
            description="Test description",
            url="http://localhost:8001",
            port=8001,
            version="2.1.0",
        )

        # Then: カスタムバージョンが設定される
        assert config.version == "2.1.0"

    def test_port_boundary_values(self):
        """ポート境界値テスト"""
        # Given/When: 最小有効ポート（1）で作成
        config = AgentConfig(
            name="test-agent",
            description="Test description",
            url="http://localhost:1",
            port=1,  # 最小有効値
        )

        # Then: 正常に作成される
        assert config.port == 1

        # Given/When: 一般的な大きなポート（65535）で作成
        config_large = AgentConfig(
            name="test-agent",
            description="Test description",
            url="http://localhost:65535",
            port=65535,  # 大きな有効値
        )

        # Then: 正常に作成される
        assert config_large.port == 65535
