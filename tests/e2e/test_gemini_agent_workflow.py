"""
適切なE2Eテスト設計例 - エラー種別判定とリトライロジック

問題:
- エラー種別を区別せずに一律スキップ
- レート制限とセーフティフィルタの区別なし
- リトライロジックの欠如

改善:
- 適切なエラー分類
- レート制限時のリトライ
- セーフティフィルタ時のクエリ改善
- ネットワークエラーのハンドリング
"""

import asyncio
import logging
import os
from typing import Optional, Tuple

import pytest
from dotenv import load_dotenv
from google.generativeai.types import BlockedPromptException

from app.a2a_prototype.agents.gemini_agent import GeminiA2AAgent
from app.a2a_prototype.utils.config import AgentConfig
from app.a2a_prototype.utils.gemini_config import GeminiConfig

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
pytestmark = pytest.mark.skipif(
    not GEMINI_API_KEY,
    reason="GEMINI_API_KEY environment variable is required for E2E tests",
)


class APIErrorType:
    """API エラーの種別定義"""

    RATE_LIMIT = "rate_limit"
    SAFETY_FILTER = "safety_filter"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class RobustE2ETestHelper:
    """堅牢なE2Eテストのためのヘルパークラス"""

    MAX_RETRIES = 3
    RETRY_DELAY = 2.0  # 秒

    # セーフティフィルタ回避用の代替クエリ
    SAFE_TEST_QUERIES = [
        "Hello, how are you?",
        "What is 2 + 2?",
        "Tell me about the weather",
        "What is AI?",
        "How do computers work?",
    ]

    @staticmethod
    def classify_error(
        response: str, exception: Optional[Exception] = None
    ) -> str:
        """エラーの種別を分類"""
        if exception:
            if isinstance(exception, BlockedPromptException):
                return APIErrorType.SAFETY_FILTER
            exception_str = str(exception).lower()
            if "rate" in exception_str or "quota" in exception_str:
                return APIErrorType.RATE_LIMIT
            if "network" in exception_str or "connection" in exception_str:
                return APIErrorType.NETWORK_ERROR

        if response:
            response_lower = response.lower()
            if "rate limit" in response_lower or "quota" in response_lower:
                return APIErrorType.RATE_LIMIT
            if "safety" in response_lower or "harmful" in response_lower:
                return APIErrorType.SAFETY_FILTER
            if "ネットワーク" in response or "接続" in response:
                return APIErrorType.NETWORK_ERROR

        return APIErrorType.UNKNOWN

    @staticmethod
    async def execute_with_retry(
        agent: GeminiA2AAgent, query: str
    ) -> Tuple[str, bool]:
        """
        リトライロジック付きでクエリを実行

        Returns:
            (response, success): レスポンスと成功フラグ
        """
        original_query = query

        for attempt in range(RobustE2ETestHelper.MAX_RETRIES):
            try:
                response = await agent.process_user_input(query)

                # 成功判定
                if (
                    response
                    and len(response) > 0
                    and "申し訳ございません" not in response
                    and "error" not in response.lower()
                ):
                    return response, True

                # エラー分類
                error_type = RobustE2ETestHelper.classify_error(response)

                if error_type == APIErrorType.RATE_LIMIT:
                    delay = RobustE2ETestHelper.RETRY_DELAY
                    logging.warning(
                        "Rate limit detected, retrying in %ss...", delay
                    )
                    await asyncio.sleep(delay)
                    continue

                elif error_type == APIErrorType.SAFETY_FILTER:
                    safe_queries = RobustE2ETestHelper.SAFE_TEST_QUERIES
                    if attempt < len(safe_queries):
                        query = safe_queries[attempt]
                        logging.warning(
                            "Safety filter detected, trying safer query: %s",
                            query,
                        )
                        continue
                    else:
                        return (
                            "SAFETY_FILTER_ERROR: All safe queries failed",
                            False,
                        )

                elif error_type == APIErrorType.NETWORK_ERROR:
                    logging.warning("Network error detected, retrying...")
                    await asyncio.sleep(RobustE2ETestHelper.RETRY_DELAY)
                    continue

                else:
                    return f"UNKNOWN_ERROR: {response}", False

            except Exception as e:
                error_type = RobustE2ETestHelper.classify_error("", e)

                if (
                    error_type == APIErrorType.RATE_LIMIT
                    and attempt < RobustE2ETestHelper.MAX_RETRIES - 1
                ):
                    delay = RobustE2ETestHelper.RETRY_DELAY
                    logging.warning(
                        "Rate limit exception, retrying in %ss...", delay
                    )
                    await asyncio.sleep(delay)
                    continue

                return f"EXCEPTION_ERROR: {str(e)}", False

        return f"MAX_RETRIES_EXCEEDED: Original query: {original_query}", False


class TestRobustGeminiAgentE2E:
    """改善されたGemini A2A Agent エンドツーエンドテスト"""

    @pytest.fixture
    def real_configs(self):
        """実際のAPIキーを使用した設定"""
        agent_config = AgentConfig(
            name="robust-test-gemini-agent",
            description="Robust E2E test agent with proper error handling",
            url="http://localhost:8005",
            port=8005,
        )

        gemini_config = GeminiConfig(
            api_key=GEMINI_API_KEY,
            model="gemini-2.5-pro-preview-05-06",
            temperature=0.3,  # より一貫した応答のため低めに設定
            max_tokens=200,  # テスト用に短めに設定
        )

        return agent_config, gemini_config

    @pytest.mark.asyncio
    async def test_robust_api_connection(self, real_configs):
        """堅牢なAPI接続テスト"""
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # ヘルスチェックを複数回試行
        for attempt in range(3):
            try:
                health = await agent.gemini_client.health_check()
                if health:
                    break
                await asyncio.sleep(1.0)
            except Exception:
                if attempt == 2:
                    pytest.fail("API connection failed after 3 attempts")
                await asyncio.sleep(1.0)

        assert health is True, "Gemini API health check should pass"

    @pytest.mark.asyncio
    async def test_robust_simple_conversation(self, real_configs):
        """堅牢な基本対話テスト"""
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        response, success = await RobustE2ETestHelper.execute_with_retry(
            agent, "Hello, how are you?"
        )

        # 成功した場合のアサーション
        if success:
            assert response is not None
            assert len(response) > 0
            print(f"✅ Successful response: {response}")
        else:
            # 失敗した場合は詳細を報告して適切に失敗
            if "SAFETY_FILTER_ERROR" in response:
                fail_msg = (
                    "Safety filter rejected all safe test queries "
                    "- configuration issue"
                )
                pytest.fail(fail_msg)
            elif "RATE_LIMIT" in response:
                fail_msg = (
                    "Rate limit exceeded even with retries "
                    "- API quota issue"
                )
                pytest.fail(fail_msg)
            elif "NETWORK_ERROR" in response:
                fail_msg = (
                    "Network connectivity issues " "- infrastructure problem"
                )
                pytest.fail(fail_msg)
            else:
                pytest.fail(f"Unexpected API failure: {response}")

    @pytest.mark.asyncio
    async def test_robust_conversation_context(self, real_configs):
        """堅牢な会話コンテキストテスト"""
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # 第1回の対話
        response1, success1 = await RobustE2ETestHelper.execute_with_retry(
            agent, "My name is TestUser"
        )

        if not success1:
            pytest.fail(f"First conversation failed: {response1}")

        # 第2回の対話（コンテキスト確認）
        response2, success2 = await RobustE2ETestHelper.execute_with_retry(
            agent, "What is my name?"
        )

        if not success2:
            pytest.fail(f"Second conversation failed: {response2}")

        # 両方成功した場合のみコンテキストチェック
        assert len(agent.conversation_context) == 4  # 2往復分
        assert "TestUser" in response2 or "testuser" in response2.lower()

    @pytest.mark.asyncio
    async def test_command_reliability(self, real_configs):
        """コマンド系機能の信頼性テスト"""
        agent_config, gemini_config = real_configs
        agent = GeminiA2AAgent(agent_config, gemini_config)

        # ヘルプコマンド（APIを使わないためエラーが起きにくい）
        help_response = await agent.process_user_input("help")
        assert "Gemini 2.5 Pro搭載エージェント" in help_response

        # ステータスコマンド
        status_response = await agent.process_user_input("status")
        assert "robust-test-gemini-agent" in status_response

        # クリアコマンド
        clear_response = await agent.process_user_input("clear")
        assert "会話履歴をクリアしました" in clear_response
