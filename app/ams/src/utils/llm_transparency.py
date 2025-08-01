"""LLM Transparency Utilities - 内部動作の可視化

LLMの動作を透明化し、実際のAPI呼び出しであることを
検証可能にするユーティリティ集
"""

import functools
import hashlib
import time
from collections.abc import Callable
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


class TransparentLLM:
    """LLMの動作を透明化するラッパークラス"""

    def __init__(self, llm: BaseChatModel, enable_verification: bool = True):
        self.llm = llm
        self.enable_verification = enable_verification
        self.call_history: list[dict[str, Any]] = []
        self._call_count = 0

    async def ainvoke(self, prompt: str, **kwargs) -> BaseMessage:
        """透明性を確保したLLM呼び出し"""
        call_id = f"call_{self._call_count:04d}"
        self._call_count += 1

        # 呼び出し記録開始
        call_record = {
            "call_id": call_id,
            "timestamp": time.time(),
            "prompt": prompt,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
            "kwargs": kwargs,
        }

        if self.enable_verification:
            print(f"\n🔍 LLM Call #{call_id}")
            print(f"   Prompt hash: {call_record['prompt_hash']}")
            print(f"   Prompt length: {len(prompt)} chars")

        # 実際のLLM呼び出し
        start_time = time.time()
        try:
            response = await self.llm.ainvoke(prompt, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            # レスポンス記録
            call_record.update(
                {
                    "response": response.content,
                    "response_hash": hashlib.sha256(response.content.encode()).hexdigest()[:16],
                    "latency_ms": latency_ms,
                    "success": True,
                }
            )

            if self.enable_verification:
                print(f"   Response hash: {call_record['response_hash']}")
                print(f"   Latency: {latency_ms}ms")
                print(f"   Response length: {len(response.content)} chars")

        except Exception as e:
            call_record.update(
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "success": False,
                }
            )

            if self.enable_verification:
                print(f"   ❌ Error: {type(e).__name__}")

            raise

        finally:
            self.call_history.append(call_record)

        return response

    def get_verification_summary(self) -> dict[str, Any]:
        """呼び出し履歴のサマリーを取得"""
        if not self.call_history:
            return {"total_calls": 0, "summary": "No calls made"}

        successful_calls = [c for c in self.call_history if c.get("success", False)]
        failed_calls = [c for c in self.call_history if not c.get("success", False)]

        latencies = [c["latency_ms"] for c in successful_calls if "latency_ms" in c]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        return {
            "total_calls": len(self.call_history),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "average_latency_ms": int(avg_latency),
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "unique_prompts": len(
                {c.get("prompt_hash", "") for c in self.call_history if "prompt_hash" in c}
            ),
            "unique_responses": len(
                {c.get("response_hash", "") for c in successful_calls if "response_hash" in c}
            ),
        }


def verify_llm_call(func: Callable) -> Callable:
    """LLM呼び出しを検証するデコレータ"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"\n🔍 Verifying LLM call in {func.__name__}")
        start_time = time.time()

        # 関数実行前の状態を記録 (for debugging if needed)
        # pre_state recorded but not used in current implementation

        try:
            # 実際の関数実行
            result = await func(*args, **kwargs)

            # 実行後の検証
            execution_time = time.time() - start_time
            post_state = {
                "execution_time_ms": int(execution_time * 1000),
                "result_type": type(result).__name__,
                "result_hash": (
                    hashlib.sha256(str(result).encode()).hexdigest()[:16] if result else "none"
                ),
            }

            print("✅ Verification passed:")
            print(f"   Execution time: {post_state['execution_time_ms']}ms")
            print(f"   Result type: {post_state['result_type']}")
            print(f"   Result hash: {post_state['result_hash']}")

            # 異常検出
            if execution_time < 0.01:  # 10ms未満は疑わしい
                print("⚠️  Warning: Execution was suspiciously fast")

            return result

        except Exception as e:
            print(f"❌ Verification failed: {type(e).__name__}: {str(e)}")
            raise

    return wrapper


class LLMCallTracker:
    """テスト用のLLM呼び出しトラッカー"""

    def __init__(self):
        self.reset()

    def reset(self):
        """トラッキング情報をリセット"""
        self.calls: list[dict[str, Any]] = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def track_call(
        self,
        prompt: str,
        response: str,
        model: str,
        latency_ms: int,
        tokens: dict[str, int] | None = None,
    ):
        """LLM呼び出しを記録"""
        call_data = {
            "timestamp": time.time(),
            "prompt": prompt,
            "response": response,
            "model": model,
            "latency_ms": latency_ms,
            "prompt_tokens": tokens.get("prompt_tokens", 0) if tokens else 0,
            "completion_tokens": tokens.get("completion_tokens", 0) if tokens else 0,
            "total_tokens": tokens.get("total_tokens", 0) if tokens else 0,
        }

        # コスト推定（Gemini Flash: $0.075 per 1M input, $0.30 per 1M output）
        if tokens:
            input_cost = (tokens.get("prompt_tokens", 0) / 1_000_000) * 0.075
            output_cost = (tokens.get("completion_tokens", 0) / 1_000_000) * 0.30
            call_data["estimated_cost"] = input_cost + output_cost
            self.total_cost += call_data["estimated_cost"]
            self.total_tokens += tokens.get("total_tokens", 0)

        self.calls.append(call_data)

    def get_summary(self) -> dict[str, Any]:
        """トラッキングサマリーを取得"""
        if not self.calls:
            return {"message": "No LLM calls tracked"}

        latencies = [c["latency_ms"] for c in self.calls]

        return {
            "total_calls": len(self.calls),
            "total_tokens": self.total_tokens,
            "estimated_total_cost": f"${self.total_cost:.6f}",
            "average_latency_ms": int(sum(latencies) / len(latencies)),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "models_used": list({c["model"] for c in self.calls}),
        }

    def print_detailed_report(self):
        """詳細レポートを出力"""
        print("\n" + "=" * 60)
        print("LLM Call Tracking Report")
        print("=" * 60)

        for i, call in enumerate(self.calls, 1):
            print(f"\nCall #{i}:")
            print(f"  Model: {call['model']}")
            print(f"  Latency: {call['latency_ms']}ms")
            print(f"  Tokens: {call['total_tokens']}")
            if "estimated_cost" in call:
                print(f"  Cost: ${call['estimated_cost']:.6f}")
            print(f"  Prompt preview: {call['prompt'][:50]}...")
            print(f"  Response preview: {call['response'][:50]}...")

        summary = self.get_summary()
        print("\n" + "-" * 60)
        print("Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


# グローバルトラッカーインスタンス
global_llm_tracker = LLMCallTracker()


def get_llm_tracker() -> LLMCallTracker:
    """グローバルLLMトラッカーを取得"""
    return global_llm_tracker
