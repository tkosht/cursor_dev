"""
Unit tests for configuration management
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from config import (
    AMSConfig,
    LLMConfig,
    PerformanceConfig,
    SimulationConfig,
)
from config.llm_selector import (
    MODEL_CAPABILITIES,
    LLMProvider,
    LLMSelector,
    TaskType,
    select_optimal_llm,
)


class TestLLMConfig:
    """Test LLM configuration"""

    def test_default_config(self):
        """Test default LLM config"""
        config = LLMConfig()

        assert config.provider == "gemini"
        assert config.gemini_model == "gemini-2.5-flash"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_config_with_api_key(self, monkeypatch):
        """Test config with API key from environment"""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

        config = LLMConfig(provider="gemini", google_api_key=os.getenv("GOOGLE_API_KEY"))

        assert config.google_api_key == "test-google-key"

    def test_invalid_provider_without_key(self, monkeypatch):
        """Test invalid provider without API key"""
        # 環境変数をクリア
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key required"):
            LLMConfig(provider="openai", openai_api_key=None)


class TestSimulationConfig:
    """Test simulation configuration"""

    def test_default_config(self):
        """Test default simulation config"""
        config = SimulationConfig()

        assert config.max_personas == 100
        assert config.max_simulation_steps == 50
        assert config.population_size == 50
        assert config.enable_micro_behaviors is True

    def test_config_validation(self):
        """Test config validation"""
        # Valid config
        config = SimulationConfig(max_personas=50, population_size=25)
        assert config.max_personas == 50

        # Invalid config (negative values)
        with pytest.raises(ValueError):
            SimulationConfig(max_personas=-1)


class TestAMSConfig:
    """Test main AMS configuration"""

    def test_from_env(self, monkeypatch):
        """Test creating config from environment"""
        # Set environment variables
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("AMS_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("AMS_MAX_PERSONAS", "75")
        monkeypatch.setenv("TEST_MODE", "true")

        config = AMSConfig.from_env()

        assert config.log_level == "DEBUG"
        assert config.test_mode is True
        assert config.llm.provider == "gemini"
        assert config.simulation.max_personas == 75

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = AMSConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "app_name" in config_dict
        assert "llm" in config_dict
        assert "simulation" in config_dict
        assert isinstance(config_dict["llm"], dict)


class TestLLMSelector:
    """Test LLM automatic selection"""

    def test_selector_initialization(self):
        """Test selector initialization"""
        selector = LLMSelector([LLMProvider.GEMINI, LLMProvider.OPENAI])

        assert LLMProvider.GEMINI in selector.available_providers
        assert LLMProvider.OPENAI in selector.available_providers
        assert len(selector.model_capabilities) > 0

    def test_select_model_basic(self):
        """Test basic model selection"""
        selector = LLMSelector([LLMProvider.GEMINI])

        model, capabilities = selector.select_model(
            task_type=TaskType.ANALYSIS,
            min_quality=8.0,
            min_speed=8.0,
        )

        assert model in MODEL_CAPABILITIES
        assert capabilities.provider == LLMProvider.GEMINI
        assert capabilities.quality >= 8.0
        assert capabilities.speed >= 8.0

    def test_select_model_with_features(self):
        """Test model selection with required features"""
        selector = LLMSelector([LLMProvider.GEMINI, LLMProvider.OPENAI])

        model, capabilities = selector.select_model(
            task_type=TaskType.GENERATION,
            required_features=["json_mode", "function_calling"],
        )

        assert capabilities.supports_json_mode is True
        assert capabilities.supports_function_calling is True

    def test_select_model_with_cost_constraint(self):
        """Test model selection with cost constraint"""
        selector = LLMSelector([LLMProvider.GEMINI, LLMProvider.OPENAI])

        model, capabilities = selector.select_model(
            task_type=TaskType.SUMMARIZATION,
            max_cost_per_1k=0.0002,  # Very low cost
        )

        assert capabilities.cost_per_1k_tokens <= 0.0002

    def test_select_model_fallback(self):
        """Test fallback when no suitable model found"""
        selector = LLMSelector([])  # No available providers

        model, capabilities = selector.select_model(
            task_type=TaskType.REASONING,
        )

        # Should fallback to default
        assert model == "gemini-2.5-flash"

    def test_estimate_cost(self):
        """Test cost estimation"""
        selector = LLMSelector()

        cost = selector.estimate_cost(
            model_name="gpt-4o",
            input_tokens=1000,
            output_tokens=500,
        )

        expected_cost = (1500 / 1000) * MODEL_CAPABILITIES["gpt-4o"].cost_per_1k_tokens
        assert cost == pytest.approx(expected_cost)

    def test_provider_preference(self):
        """Test provider preference in selection"""
        selector = LLMSelector([LLMProvider.GEMINI, LLMProvider.OPENAI])

        # Without preference
        model1, _ = selector.select_model(
            task_type=TaskType.ANALYSIS,
            min_quality=8.0,
        )

        # With preference
        model2, capabilities2 = selector.select_model(
            task_type=TaskType.ANALYSIS,
            min_quality=8.0,
            prefer_provider=LLMProvider.OPENAI,
        )

        # Should prefer OpenAI when specified
        assert capabilities2.provider == LLMProvider.OPENAI


class TestLLMSelectorIntegration:
    """Test LLM selector integration with config"""

    @patch("config.config.get_config")
    def test_select_optimal_llm(self, mock_get_config):
        """Test the convenience function"""
        # Mock config
        mock_config = MagicMock()
        mock_config.llm.google_api_key = "test-key"
        mock_config.llm.openai_api_key = None
        mock_config.llm.anthropic_api_key = None
        mock_config.llm.provider = "gemini"
        mock_get_config.return_value = mock_config

        provider, model = select_optimal_llm(
            task_type=TaskType.CREATIVE,
            required_features=["json_mode"],
        )

        assert provider == "gemini"
        assert model in ["gemini-2.5-flash", "gemini-2.5-pro"]


class TestPerformanceConfig:
    """Test performance configuration"""

    def test_directory_creation(self, tmp_path):
        """Test that directories are created"""
        cache_dir = tmp_path / "cache"
        profile_dir = tmp_path / "profile"

        PerformanceConfig(
            cache_dir=cache_dir,
            profile_output_dir=profile_dir,
        )

        assert cache_dir.exists()
        assert profile_dir.exists()

    def test_default_values(self):
        """Test default performance config values"""
        config = PerformanceConfig()

        assert config.parallel_workers == 10
        assert config.enable_caching is True
        assert config.batch_processing is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
