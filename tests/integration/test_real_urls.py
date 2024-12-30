"""
実際のURLでの動作確認テスト
"""
import asyncio
import logging
import os
from typing import Dict, List

import pytest
from dotenv import load_dotenv

from app.llm.manager import LLMManager

# ログ設定
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# テストモジュール全体のログレベルを設定
logging.getLogger("app").setLevel(logging.DEBUG)
logging.getLogger("tests").setLevel(logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)

# 非同期処理のデバッグを有効化
asyncio.get_event_loop().set_debug(True)

# テスト用のURL一覧
TEST_URLS = [
    {
        "url": "https://www.softbank.jp/corp/about/",
        "path": ["corp", "about"],
        "expected_category": "company_profile",
    },
    {
        "url": "https://www.toyota.co.jp/jpn/company/",
        "path": ["jpn", "company"],
        "expected_category": "company_profile",
    },
    {
        "url": "https://www.accenture.com/jp-ja/about/company-index",
        "path": ["jp-ja", "about", "company-index"],
        "expected_category": "company_profile",
    },
]

# テスト設定
TIMEOUT_SECONDS = 30  # テストのタイムアウト時間
RATE_LIMIT_TEST_COUNT = 2  # レート制限テストの回数を削減


@pytest.fixture(scope="module")
def event_loop():
    """イベントループのフィクスチャ"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def llm_manager() -> LLMManager:
    """LLMマネージャーのフィクスチャ"""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY_GEMINI not set")

    manager = LLMManager()
    manager = await manager.load_model("gemini-2.0-flash-exp", api_key)
    return manager


@pytest.mark.asyncio
async def test_real_url_analysis(llm_manager: LLMManager):
    """実際のURLの分析テスト"""
    logger.debug("Starting test_real_url_analysis")

    # フィクスチャをawait
    manager = await llm_manager

    for test_case in TEST_URLS:
        logger.info(f"Testing URL: {test_case['url']}")
        logger.debug(f"Test case details: {test_case}")

        try:
            logger.debug("Preparing to execute URL analysis")
            # URL分析を実行（タイムアウト付き）
            result = await asyncio.wait_for(
                manager.evaluate_url_relevance(
                    url=test_case["url"],
                    path_components=test_case["path"],
                    query_params={},
                ),
                timeout=TIMEOUT_SECONDS,
            )
            logger.debug(f"Analysis result: {result}")

            # 結果を検証
            assert result is not None, f"Failed to analyze URL: {test_case['url']}"
            logger.debug("Validating category")
            assert (
                result["category"] == test_case["expected_category"]
            ), f"Unexpected category for {test_case['url']}: {result['category']}"
            logger.debug("Validating relevance score")
            assert (
                0 <= result["relevance_score"] <= 1
            ), f"Invalid relevance score: {result['relevance_score']}"
            logger.debug("Validating confidence score")
            assert (
                0 <= result["confidence"] <= 1
            ), f"Invalid confidence score: {result['confidence']}"
            logger.debug("Validating reason")
            assert result["reason"], "Reason should not be empty"

            # レイテンシを確認
            logger.debug("Checking latency")
            latency = manager.llm.get_llm_latency()
            assert latency > 0, f"Invalid latency: {latency}"
            logger.info(f"Analysis completed in {latency:.2f}s")

            # 次のリクエストの前に少し待機
            logger.debug("Waiting before next request")
            await asyncio.sleep(1)

        except asyncio.TimeoutError:
            logger.error(
                f"Timeout analyzing URL {test_case['url']} after {TIMEOUT_SECONDS}s"
            )
            raise
        except Exception as e:
            logger.error(
                f"Error analyzing URL {test_case['url']}: {str(e)}", exc_info=True
            )
            raise


@pytest.mark.asyncio
async def test_error_handling(llm_manager: LLMManager):
    """エラーハンドリングのテスト"""
    logger.debug("Starting test_error_handling")

    # フィクスチャをawait
    manager = await llm_manager

    try:
        # 存在しないドメインのテスト
        logger.debug("Testing nonexistent domain")
        result = await asyncio.wait_for(
            manager.evaluate_url_relevance(
                url="https://nonexistent.example.com",
                path_components=["error"],
                query_params={},
            ),
            timeout=TIMEOUT_SECONDS,
        )
        logger.debug(f"Nonexistent domain test result: {result}")
        assert result is not None
        assert result["category"] == "other"
        assert result["confidence"] < 0.5

        await asyncio.sleep(1)  # レート制限を避けるために待機

        # レート制限のテスト（回数を削減）
        results: List[Dict] = []
        for i in range(RATE_LIMIT_TEST_COUNT):
            result = await manager.evaluate_url_relevance(
                url=f"https://example.com/test{i}",
                path_components=["test"],
                query_params={},
            )
            assert result is not None
            results.append(result)
            await asyncio.sleep(1)  # レート制限を避けるために待機

        # 全てのリクエストが処理されたことを確認
        assert len(results) == RATE_LIMIT_TEST_COUNT

        # レイテンシの変動を確認
        latencies = [
            manager.llm.get_llm_latency() for _ in range(RATE_LIMIT_TEST_COUNT)
        ]
        assert all(lat > 0 for lat in latencies)
        logger.info(f"Latency variation: {min(latencies):.2f}s - {max(latencies):.2f}s")

    except asyncio.TimeoutError:
        logger.error("Timeout in error handling test")
        raise
    except Exception as e:
        logger.error(f"Error in error handling test: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_redirect_handling(llm_manager: LLMManager):
    """リダイレクトを含むURLの処理テスト"""
    logger.debug("Starting test_redirect_handling")

    # フィクスチャをawait
    manager = await llm_manager

    # HTTPからHTTPSへのリダイレクトテスト
    test_urls = [
        {
            "url": "http://www.softbank.jp/corp/about/",
            "expected_category": "company_profile",
        },
        {
            "url": "http://www.toyota.co.jp/jpn/company/",
            "expected_category": "company_profile",
        },
    ]

    for test_case in test_urls:
        logger.info(f"Testing redirect URL: {test_case['url']}")

        try:
            result = await asyncio.wait_for(
                manager.evaluate_url_relevance(
                    url=test_case["url"],
                    path_components=test_case["url"].split("/")[3:],
                    query_params={},
                ),
                timeout=TIMEOUT_SECONDS,
            )

            assert result is not None
            assert result["category"] == test_case["expected_category"]
            assert result["confidence"] > 0.5

            await asyncio.sleep(1)  # レート制限を避けるために待機

        except Exception as e:
            logger.error(f"Error testing redirect URL {test_case['url']}: {str(e)}")
            raise


@pytest.mark.asyncio
async def test_ir_info_pages(llm_manager: LLMManager):
    """IR情報ページの分析テスト"""
    logger.debug("Starting test_ir_info_pages")

    # フィクスチャをawait
    manager = await llm_manager

    ir_test_urls = [
        {
            "url": "https://www.softbank.jp/corp/ir/",
            "path": ["corp", "ir"],
            "expected_category": "ir_info",
        },
        {
            "url": "https://global.toyota/jp/ir/",
            "path": ["jp", "ir"],
            "expected_category": "ir_info",
        },
    ]

    for test_case in ir_test_urls:
        logger.info(f"Testing IR URL: {test_case['url']}")

        try:
            result = await asyncio.wait_for(
                manager.evaluate_url_relevance(
                    url=test_case["url"],
                    path_components=test_case["path"],
                    query_params={},
                ),
                timeout=TIMEOUT_SECONDS,
            )

            assert result is not None
            assert result["category"] == test_case["expected_category"]
            assert result["confidence"] > 0.5
            assert "IR" in result["reason"] or "投資家" in result["reason"]

            # メトリクスの確認
            latency = manager.llm.get_llm_latency()
            assert latency > 0
            logger.info(f"IR page analysis completed in {latency:.2f}s")

            await asyncio.sleep(1)  # レート制限を避けるために待機

        except Exception as e:
            logger.error(f"Error testing IR URL {test_case['url']}: {str(e)}")
            raise


@pytest.mark.asyncio
async def test_performance_metrics(llm_manager: LLMManager):
    """パフォーマンスメトリクスのテスト"""
    logger.debug("Starting test_performance_metrics")

    # フィクスチャをawait
    manager = await llm_manager

    test_url = "https://www.softbank.jp/corp/about/"

    try:
        # メトリクスの初期状態を記録
        initial_prompt_tokens = manager.llm.metrics.prompt_tokens
        initial_completion_tokens = manager.llm.metrics.completion_tokens
        initial_error_count = manager.llm.metrics.error_count

        # URL分析を実行
        await asyncio.wait_for(
            manager.evaluate_url_relevance(
                url=test_url,
                path_components=["corp", "about"],
                query_params={},
            ),
            timeout=TIMEOUT_SECONDS,
        )

        # メトリクスの更新を確認
        assert manager.llm.metrics.prompt_tokens > initial_prompt_tokens
        assert manager.llm.metrics.completion_tokens > initial_completion_tokens
        assert manager.llm.metrics.error_count == initial_error_count

        # レイテンシの確認
        latency = manager.llm.get_llm_latency()
        assert latency > 0
        logger.info(f"Performance test completed in {latency:.2f}s")

    except Exception as e:
        logger.error(f"Error in performance metrics test: {str(e)}")
        raise
