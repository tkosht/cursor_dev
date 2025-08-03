"""
Configuration management for AMS
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, cast

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration"""

    provider: Literal["gemini", "openai", "anthropic"] = Field(
        default="gemini", description="LLM provider to use"
    )

    # Gemini settings
    google_api_key: str | None = Field(default=None, description="Google API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model name")

    # OpenAI settings
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")

    # Anthropic settings
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307", description="Anthropic model name"
    )

    # Common settings
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    timeout: int = Field(default=60, gt=0, description="Request timeout in seconds")

    @validator("provider")
    def validate_api_key(cls, v: str, values: dict[str, Any]) -> str:
        """Ensure API key exists for selected provider"""
        key_map = {
            "gemini": "google_api_key",
            "openai": "openai_api_key",
            "anthropic": "anthropic_api_key",
        }

        api_key = values.get(key_map[v])
        if not api_key:
            # Try to get from environment
            env_key_map = {
                "gemini": "GOOGLE_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }
            api_key = os.getenv(env_key_map[v])

        if not api_key:
            raise ValueError(f"API key required for provider {v}")

        return v


class SimulationConfig(BaseModel):
    """Simulation configuration"""

    max_personas: int = Field(default=100, gt=0, le=1000)
    max_simulation_steps: int = Field(default=50, gt=0, le=500)
    population_size: int = Field(default=50, gt=0, le=100)

    # Persona generation settings
    persona_generation_batch_size: int = Field(default=10, gt=0)
    enable_micro_behaviors: bool = Field(default=True)
    enable_network_effects: bool = Field(default=True)

    # Simulation behavior
    convergence_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    early_stopping: bool = Field(default=True)
    random_seed: int | None = Field(default=None)


class VisualizationConfig(BaseModel):
    """Visualization configuration"""

    enabled: bool = Field(default=True)
    websocket_host: str = Field(default="0.0.0.0")
    websocket_port: int = Field(default=8765, gt=0, lt=65536)
    max_connections: int = Field(default=100, gt=0)

    # Update settings
    update_interval: float = Field(default=0.5, gt=0.0, description="Update interval in seconds")
    use_differential_updates: bool = Field(default=True)
    compress_updates: bool = Field(default=True)

    # Visualization options
    show_network_graph: bool = Field(default=True)
    show_time_series: bool = Field(default=True)
    show_heatmaps: bool = Field(default=True)
    show_sentiment_flow: bool = Field(default=True)


class PerformanceConfig(BaseModel):
    """Performance configuration"""

    parallel_workers: int = Field(default=10, gt=0, le=50)
    enable_caching: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, gt=0, description="Cache TTL in seconds")
    cache_dir: Path = Field(default=Path(".cache"))

    # Profiling
    enable_profiling: bool = Field(default=False)
    profile_output_dir: Path = Field(default=Path("logs/performance"))

    # Resource limits
    max_memory_mb: int = Field(default=4096, gt=0)
    request_timeout: int = Field(default=60, gt=0)

    # Optimization
    batch_processing: bool = Field(default=True)
    adaptive_sampling: bool = Field(default=True)

    @validator("cache_dir", "profile_output_dir")
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist"""
        v.mkdir(parents=True, exist_ok=True)
        return v


class AMSConfig(BaseSettings):
    """Main AMS configuration"""

    # Application settings
    app_name: str = Field(default="Article Market Simulator")
    log_level: str = Field(default="INFO")
    debug_mode: bool = Field(default=False)

    # Sub-configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    # Testing
    test_mode: bool = Field(default=False)
    test_max_cost: float = Field(default=10.0, gt=0.0)

    class Config:
        env_prefix = "AMS_"
        env_nested_delimiter = "__"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "AMSConfig":
        """Create config from environment variables"""
        # Load LLM config from env
        # Auto-detect provider based on available API keys
        provider = os.getenv("LLM_PROVIDER")
        if not provider:
            # Auto-detect based on available API keys
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
                provider = "gemini"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            else:
                provider = "gemini"  # Default, will fail validation if no key

        llm_config = LLMConfig(
            provider=cast(
                Literal["gemini", "openai", "anthropic"],
                provider,
            ),
            google_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
        )

        # Load other configs
        sim_config = SimulationConfig(
            max_personas=int(os.getenv("AMS_MAX_PERSONAS", "100")),
            max_simulation_steps=int(os.getenv("AMS_MAX_SIMULATION_STEPS", "50")),
        )

        viz_config = VisualizationConfig(
            websocket_host=os.getenv("WEBSOCKET_HOST", "0.0.0.0"),
            websocket_port=int(os.getenv("WEBSOCKET_PORT", "8765")),
        )

        perf_config = PerformanceConfig(
            parallel_workers=int(os.getenv("AMS_PARALLEL_WORKERS", "10")),
            enable_caching=os.getenv("ENABLE_CACHE", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
        )

        return cls(
            log_level=os.getenv("AMS_LOG_LEVEL", "INFO"),
            test_mode=os.getenv("TEST_MODE", "false").lower() == "true",
            llm=llm_config,
            simulation=sim_config,
            visualization=viz_config,
            performance=perf_config,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "app_name": self.app_name,
            "log_level": self.log_level,
            "debug_mode": self.debug_mode,
            "llm": self.llm.model_dump(),
            "simulation": self.simulation.model_dump(),
            "visualization": self.visualization.model_dump(),
            "performance": self.performance.model_dump(),
            "test_mode": self.test_mode,
        }


# Global config instance
_config: AMSConfig | None = None


@lru_cache(maxsize=1)
def get_config() -> AMSConfig:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = AMSConfig.from_env()
    return _config


def load_config(config_path: Path | None = None) -> AMSConfig:
    """Load config from file or environment"""
    if config_path and config_path.exists():
        # Load from JSON/YAML file
        import json

        with open(config_path) as f:
            config_data = json.load(f)
        return AMSConfig(**config_data)
    else:
        # Load from environment
        return AMSConfig.from_env()
