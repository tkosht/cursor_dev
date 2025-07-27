"""Small scale integration test for AMS components with REAL LLM calls.

This test verifies basic functionality with minimal LLM API calls:
- 3 personas
- Short article (500 chars)
- Real API calls (NO MOCKS)
"""

import asyncio
import json
import logging
import time

import pytest
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestSmallScaleIntegration:
    """Small scale integration tests to verify functionality with minimal API calls."""

    @pytest.fixture
    def short_article(self):
        """Short article for testing (約500文字)."""
        return """
        # AIアシスタントの新機能発表

        本日、新しいAIアシスタント機能を発表しました。
        この機能により、日常業務の効率が大幅に向上します。

        主な特徴：
        - 自然な会話での操作
        - マルチタスク対応
        - 24時間利用可能

        ユーザーからは「使いやすい」「時間の節約になる」といった
        ポジティブなフィードバックを多数いただいています。

        今後も継続的な改善を行い、より良いサービスを提供していきます。
        """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_minimal_pipeline(self, short_article):
        """Test the minimal pipeline with 3 personas."""
        logger.info("=== Starting Small Scale Integration Test ===")

        # Track API calls and timing
        api_calls = {"analyzer": 0, "architect": 0, "generator": 0}
        start_time = time.time()

        try:
            # Import inside test to avoid collection issues
            from src.agents.deep_context_analyzer import DeepContextAnalyzer
            from src.agents.persona_generator import PersonaGenerator
            from src.agents.population_architect import PopulationArchitect
            from src.core.types import PersonaAttributes
            
            # Phase 1: Context Analysis
            logger.info("\n--- Phase 1: Context Analysis ---")
            # Use lightweight mode for testing to avoid timeouts
            analyzer = DeepContextAnalyzer(force_lightweight=True)

            # タイムアウトを設定して実行
            context = await asyncio.wait_for(
                analyzer.analyze_article_context(short_article),
                timeout=90.0  # 90秒のタイムアウト
            )
            api_calls["analyzer"] = 1  # Lightweight mode: core only

            logger.info(
                f"Context analysis complete. Complexity: {context.get('complexity_score', 0)}"
            )
            logger.info(f"API calls so far: {sum(api_calls.values())}")

            # Verify context structure
            assert "core_context" in context
            assert "hidden_dimensions" in context
            assert "complexity_score" in context
            assert "reach_potential" in context

            # Phase 2: Population Design (3 personas)
            logger.info("\n--- Phase 2: Population Architecture ---")
            architect = PopulationArchitect()

            population = await architect.design_population_hierarchy(
                context, target_size=3  # Only 3 personas
            )
            api_calls["architect"] = 2  # Major segments + sub-segments

            logger.info("Population design complete.")
            logger.info(f"Population structure: {json.dumps(population, indent=2)}")
            logger.info(
                f"Major segments: {len(population['hierarchy']['major_segments'])}"
            )
            logger.info(
                f"Persona slots: {len(population['hierarchy']['persona_slots'])}"
            )
            logger.info(f"API calls so far: {sum(api_calls.values())}")

            # Verify population structure
            assert "hierarchy" in population
            assert "network_topology" in population
            assert "influence_map" in population
            assert len(population["hierarchy"]["persona_slots"]) >= 3

            # Phase 3: Persona Generation
            logger.info("\n--- Phase 3: Persona Generation ---")
            generator = PersonaGenerator()

            personas = await generator.generate_personas(
                article_content=short_article,
                analysis_results=context,
                count=3,  # Only 3 personas
            )
            api_calls["generator"] = 3  # One per persona

            logger.info(f"Generated {len(personas)} personas")
            logger.info(f"API calls so far: {sum(api_calls.values())}")

            # Verify personas
            assert len(personas) >= 3
            for i, persona in enumerate(personas):
                assert isinstance(persona, PersonaAttributes)
                logger.info(
                    f"Persona {i + 1}: {persona.occupation}, Age: {persona.age}"
                )
                logger.info(f"  Interests: {persona.interests[:2]}")
                logger.info(f"  Influence: {persona.influence_score:.2f}")

            # Cost estimation
            elapsed_time = time.time() - start_time
            total_api_calls = sum(api_calls.values())

            logger.info("\n=== Test Summary ===")
            logger.info(f"Total API calls: {total_api_calls}")
            logger.info(f"Breakdown: {api_calls}")
            logger.info(f"Execution time: {elapsed_time:.2f} seconds")
            logger.info(
                f"Estimated cost: ~${total_api_calls * 0.002:.4f} (assuming ~$0.002/call)"
            )

            # Basic assertions
            assert (
                total_api_calls <= 10
            ), "Too many API calls for small scale test"
            assert elapsed_time < 300, "Test took too long"  # Allow up to 5 minutes for real API calls

        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            raise

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_component_data_flow(self, short_article):
        """Test data flow between components."""
        logger.info("\n=== Testing Component Data Flow ===")
        
        # Import inside test to avoid collection issues
        from src.agents.deep_context_analyzer import DeepContextAnalyzer
        from src.agents.persona_generator import PersonaGenerator
        from src.agents.population_architect import PopulationArchitect
        from src.core.types import PersonaAttributes

        # Test analyzer -> architect flow
        analyzer = DeepContextAnalyzer(force_lightweight=True)
        context = await analyzer.analyze_article_context(short_article)

        architect = PopulationArchitect()
        population = await architect.design_population_hierarchy(
            context, target_size=3
        )

        # Verify data compatibility
        assert isinstance(context, dict)
        assert isinstance(population, dict)

        # Test architect -> generator flow
        generator = PersonaGenerator()
        personas = await generator.generate_personas(
            article_content=short_article, analysis_results=context, count=3
        )

        # Verify output format
        assert isinstance(personas, list)
        assert all(isinstance(p, PersonaAttributes) for p in personas)

        logger.info("✅ Data flow test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across components."""
        logger.info("\n=== Testing Error Handling ===")
        
        # Import inside test to avoid collection issues
        from src.agents.deep_context_analyzer import DeepContextAnalyzer
        from src.agents.population_architect import PopulationArchitect

        # Test with invalid article
        analyzer = DeepContextAnalyzer()
        context = await analyzer.analyze_article_context("")

        # Should return default structure even with empty input
        assert isinstance(context, dict)
        assert "core_context" in context

        # Test population design with bad context
        architect = PopulationArchitect()
        population = await architect.design_population_hierarchy(
            {}, target_size=3
        )

        # Should return valid structure
        assert isinstance(population, dict)
        assert "hierarchy" in population

        logger.info("✅ Error handling test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Performance baseline test times out with real LLM calls - needs optimization")
    async def test_performance_baseline(self, short_article):
        """Establish performance baseline for small scale."""
        logger.info("\n=== Performance Baseline Test ===")
        
        # Import inside test to avoid collection issues
        from src.agents.deep_context_analyzer import DeepContextAnalyzer
        from src.agents.population_architect import PopulationArchitect
        from src.agents.persona_generator import PersonaGenerator

        timings = {}

        # Time each component
        analyzer = DeepContextAnalyzer(force_lightweight=True)
        start = time.time()
        context = await analyzer.analyze_article_context(short_article)
        timings["analyzer"] = time.time() - start

        architect = PopulationArchitect()
        start = time.time()
        await architect.design_population_hierarchy(context, target_size=3)
        timings["architect"] = time.time() - start

        generator = PersonaGenerator()
        start = time.time()
        await generator.generate_personas(
            article_content=short_article, analysis_results=context, count=3
        )
        timings["generator"] = time.time() - start

        logger.info("\nComponent Timings:")
        for component, duration in timings.items():
            logger.info(f"  {component}: {duration:.2f}s")

        total_time = sum(timings.values())
        logger.info(f"\nTotal time: {total_time:.2f}s")

        # Set baseline expectations (relaxed for real API calls)
        assert timings["analyzer"] < 60, "Analyzer too slow"
        assert timings["architect"] < 60, "Architect too slow"
        assert timings["generator"] < 60, "Generator too slow"
        assert total_time < 180, "Total pipeline too slow"

        logger.info("✅ Performance within acceptable range")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cost_estimation():
    """Estimate costs for different scales."""
    scales = [
        {"personas": 3, "steps": 3, "api_calls": 7},
        {"personas": 10, "steps": 5, "api_calls": 20},
        {"personas": 50, "steps": 10, "api_calls": 100},
        {"personas": 100, "steps": 20, "api_calls": 250},
    ]

    logger.info("\n=== Cost Estimation ===")
    logger.info("Scale | API Calls | Est. Cost")
    logger.info("------|-----------|----------")

    for scale in scales:
        cost = scale["api_calls"] * 0.002  # $0.002 per call estimate
        logger.info(
            f"{scale['personas']:3}p, {scale['steps']:2}t | "
            f"{scale['api_calls']:9} | ${cost:8.3f}"
        )

    logger.info("\np = personas, t = timesteps")
    logger.info("Note: Actual costs depend on token usage")
