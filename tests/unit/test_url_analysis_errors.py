"""
URL分析のエラーハンドリングのテスト
"""
import asyncio

import pytest

from app.errors.url_analysis_errors import (
    ErrorHandler,
    ExponentialBackoff,
    LLMError,
    NetworkError,
    RateLimitError,
    RetryStrategy,
    URLAnalysisError,
    ValidationError,
)


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """ネットワークエラーの処理テスト"""
        handler = ErrorHandler()
        url = "https://example.com"

        # レート制限エラー
        with pytest.raises(RateLimitError) as exc_info:
            await handler.handle_network_error(url, 429, 60.0)
        assert exc_info.value.url == url
        assert exc_info.value.retry_after == 60.0

        # サーバーエラー
        with pytest.raises(NetworkError) as exc_info:
            await handler.handle_network_error(url, 500)
        assert exc_info.value.url == url
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_llm_error_handling(self):
        """LLMエラーの処理テスト"""
        handler = ErrorHandler()
        message = "Invalid response format"
        raw_response = {"error": "format error"}

        with pytest.raises(LLMError) as exc_info:
            await handler.handle_llm_error(message, raw_response)
        assert str(exc_info.value) == f"LLM error: {message}"
        assert exc_info.value.raw_response == raw_response

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """バリデーションエラーの処理テスト"""
        handler = ErrorHandler()
        result = {"score": -1}
        reason = "Score must be between 0 and 1"

        with pytest.raises(ValidationError) as exc_info:
            await handler.handle_validation_error(result, reason)
        assert exc_info.value.result == result
        assert exc_info.value.reason == reason

    @pytest.mark.asyncio
    async def test_retry_strategy(self):
        """リトライ戦略のテスト"""
        retry_strategy = RetryStrategy(max_retries=3)
        call_count = 0

        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("https://example.com", 500)
            return "success"

        # 3回目で成功するケース
        result = await retry_strategy.execute_with_retry(failing_operation)
        assert result == "success"
        assert call_count == 3

        # 最大リトライ回数を超えるケース
        call_count = 0

        async def always_failing_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            raise NetworkError("https://example.com", 500)

        with pytest.raises(URLAnalysisError):
            await retry_strategy.execute_with_retry(always_failing_operation)
        assert call_count == 3

    def test_exponential_backoff(self):
        """指数バックオフのテスト"""
        backoff = ExponentialBackoff(
            initial=1.0,
            maximum=30.0,
            multiplier=2.0,
            jitter=0.1
        )

        # 初回の待機時間
        delay = backoff.get_delay(0)
        assert 0.9 <= delay <= 1.1  # ±10%のジッター

        # 2回目の待機時間
        delay = backoff.get_delay(1)
        assert 1.8 <= delay <= 2.2  # ±10%のジッター

        # 最大値を超えないことを確認
        delay = backoff.get_delay(10)
        assert delay <= 30.0 