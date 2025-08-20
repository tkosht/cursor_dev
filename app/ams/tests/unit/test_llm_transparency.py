"""LLM透明性ユーティリティのユニットテスト - Real LLM API calls only"""

import asyncio
from dataclasses import dataclass

import pytest

from src.utils.llm_factory import create_llm
from src.utils.llm_transparency import (
    LLMCallTracker,
    TransparentLLM,
    verify_llm_call,
)


@dataclass
class SimpleLLMResponse:
    """Simple response object for testing"""

    content: str


class TestTransparentLLM:
    """TransparentLLMクラスのテスト"""

    @pytest.fixture
    def real_llm(self):
        """Real LLM fixture using llm_factory"""
        return create_llm()

    @pytest.mark.asyncio
    async def test_transparent_llm_creation(self, real_llm):
        """TransparentLLMの作成テスト"""
        transparent_llm = TransparentLLM(real_llm, enable_verification=True)
        assert transparent_llm.llm == real_llm
        assert transparent_llm.enable_verification is True
        assert transparent_llm.call_history == []

    @pytest.mark.asyncio
    async def test_transparent_llm_invoke(self, real_llm):
        """透明な呼び出しのテスト with real LLM"""
        transparent_llm = TransparentLLM(real_llm, enable_verification=False)

        # Simple prompt to minimize API usage
        response = await transparent_llm.ainvoke("Reply with 'OK' only")

        # Real LLMが応答を返したことを確認
        assert response is not None
        assert hasattr(response, "content")
        assert len(response.content) > 0

        # 履歴が記録されていることを確認
        assert len(transparent_llm.call_history) == 1
        assert transparent_llm.call_history[0]["prompt"] == "Reply with 'OK' only"
        assert transparent_llm.call_history[0]["success"] is True

    @pytest.mark.asyncio
    async def test_transparent_llm_error_handling(self):
        """エラーハンドリングのテスト with invalid LLM"""

        # Create a broken LLM that always fails
        class BrokenLLM:
            async def ainvoke(self, prompt):
                raise Exception("Test error")

        broken_llm = BrokenLLM()
        transparent_llm = TransparentLLM(broken_llm, enable_verification=False)

        with pytest.raises(Exception, match="Test error"):
            await transparent_llm.ainvoke("test prompt")

        # エラーが履歴に記録されていることを確認
        assert len(transparent_llm.call_history) == 1
        assert transparent_llm.call_history[0]["success"] is False
        assert transparent_llm.call_history[0]["error"] == "Test error"

    def test_verification_summary(self, real_llm):
        """検証サマリーのテスト"""
        transparent_llm = TransparentLLM(real_llm)

        # 履歴なしの場合
        summary = transparent_llm.get_verification_summary()
        assert summary["total_calls"] == 0

        # 履歴を手動で追加
        transparent_llm.call_history = [
            {"success": True, "latency_ms": 100, "prompt_hash": "hash1", "response_hash": "resp1"},
            {"success": True, "latency_ms": 200, "prompt_hash": "hash2", "response_hash": "resp2"},
            {"success": False, "error": "error"},
        ]

        summary = transparent_llm.get_verification_summary()
        assert summary["total_calls"] == 3
        assert summary["successful_calls"] == 2
        assert summary["failed_calls"] == 1
        assert summary["average_latency_ms"] == 150


class TestVerifyLLMCallDecorator:
    """verify_llm_callデコレータのテスト"""

    @pytest.mark.asyncio
    async def test_verify_decorator(self, capsys):
        """デコレータの基本動作テスト"""

        @verify_llm_call
        async def test_function(x, y):
            await asyncio.sleep(0.01)  # 10ms
            return x + y

        result = await test_function(5, 3)
        assert result == 8

        # 出力を確認
        captured = capsys.readouterr()
        assert "Verifying LLM call in test_function" in captured.out
        assert "Verification passed" in captured.out

    @pytest.mark.asyncio
    async def test_verify_decorator_with_error(self, capsys):
        """エラー時のデコレータ動作テスト"""

        @verify_llm_call
        async def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await failing_function()

        captured = capsys.readouterr()
        assert "Verification failed" in captured.out


class TestLLMCallTracker:
    """LLMCallTrackerのテスト"""

    def test_tracker_initialization(self):
        """トラッカーの初期化テスト"""
        tracker = LLMCallTracker()
        assert tracker.calls == []
        assert tracker.total_tokens == 0
        assert tracker.total_cost == 0.0

    def test_track_call(self):
        """呼び出し追跡のテスト"""
        tracker = LLMCallTracker()

        tracker.track_call(
            prompt="test prompt",
            response="test response",
            model="gemini-2.5-flash",
            latency_ms=500,
            tokens={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

        assert len(tracker.calls) == 1
        assert tracker.total_tokens == 30
        assert tracker.total_cost > 0

        call = tracker.calls[0]
        assert call["prompt"] == "test prompt"
        assert call["response"] == "test response"
        assert call["model"] == "gemini-2.5-flash"
        assert call["latency_ms"] == 500

    def test_get_summary(self):
        """サマリー取得のテスト"""
        tracker = LLMCallTracker()

        # 空の場合
        summary = tracker.get_summary()
        assert summary["message"] == "No LLM calls tracked"

        # データを追加
        for i in range(3):
            tracker.track_call(
                prompt=f"prompt {i}",
                response=f"response {i}",
                model="gemini-2.5-flash",
                latency_ms=100 * (i + 1),
                tokens={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            )

        summary = tracker.get_summary()
        assert summary["total_calls"] == 3
        assert summary["total_tokens"] == 60
        assert summary["average_latency_ms"] == 200
        assert summary["min_latency_ms"] == 100
        assert summary["max_latency_ms"] == 300
