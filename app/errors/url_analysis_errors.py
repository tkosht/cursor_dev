"""
URL分析のエラーハンドリングを管理するモジュール
"""
import asyncio
import logging
import time
from typing import Any, Callable, Optional, TypeVar

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class URLAnalysisError(Exception):
    """URL分析の基底エラークラス"""
    pass


class NetworkError(URLAnalysisError):
    """ネットワーク関連エラー"""
    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        super().__init__(f"Network error for {url}: {status_code}")


class LLMError(URLAnalysisError):
    """LLM評価関連エラー"""
    def __init__(self, message: str, raw_response: Any):
        self.message = message
        self.raw_response = raw_response
        super().__init__(f"LLM error: {message}")


class ValidationError(URLAnalysisError):
    """結果検証エラー"""
    def __init__(self, result: Any, reason: str):
        self.result = result
        self.reason = reason
        super().__init__(f"Validation error: {reason}")


class RateLimitError(URLAnalysisError):
    """レート制限エラー"""
    def __init__(self, url: str, retry_after: Optional[float] = None):
        self.url = url
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for {url}"
            f" (retry after: {retry_after if retry_after else 'unknown'}s)"
        )


T = TypeVar('T')


class ExponentialBackoff:
    """指数バックオフの実装"""

    def __init__(
        self,
        initial: float = 1.0,
        maximum: float = 30.0,
        multiplier: float = 2.0,
        jitter: float = 0.1
    ):
        """
        初期化

        Args:
            initial: 初期待機時間（秒）
            maximum: 最大待機時間（秒）
            multiplier: 待機時間の乗数
            jitter: ランダム変動の範囲（0-1）
        """
        self.initial = initial
        self.maximum = maximum
        self.multiplier = multiplier
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """
        待機時間を計算

        Args:
            attempt: 試行回数（0から開始）

        Returns:
            待機時間（秒）
        """
        delay = min(
            self.initial * (self.multiplier ** attempt),
            self.maximum
        )
        # ジッター（±10%）を追加
        jitter_range = delay * self.jitter
        return delay + (time.time() % (2 * jitter_range) - jitter_range)


class RetryStrategy:
    """リトライ戦略の実装"""

    def __init__(
        self,
        max_retries: int = 3,
        backoff: Optional[ExponentialBackoff] = None
    ):
        """
        初期化

        Args:
            max_retries: 最大リトライ回数
            backoff: バックオフ戦略
        """
        self.max_retries = max_retries
        self.backoff = backoff or ExponentialBackoff()

    def _should_retry(self, error: Exception) -> bool:
        """
        リトライすべきエラーかどうかを判断

        Args:
            error: 発生したエラー

        Returns:
            リトライすべきかどうか
        """
        if isinstance(error, NetworkError):
            # 5xx系エラーのみリトライ
            return error.status_code >= 500
        elif isinstance(error, RateLimitError):
            # レート制限はリトライ
            return True
        elif isinstance(error, LLMError):
            # LLMエラーはリトライ
            return True
        return False

    async def execute_with_retry(
        self,
        operation: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        リトライ付きで処理を実行

        Args:
            operation: 実行する処理
            *args: 位置引数
            **kwargs: キーワード引数

        Returns:
            処理結果

        Raises:
            URLAnalysisError: リトライ回数を超えても成功しない場合
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                if not self._should_retry(e):
                    break

                delay = self.backoff.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)

        if isinstance(last_error, URLAnalysisError):
            raise last_error
        raise URLAnalysisError(f"Operation failed: {str(last_error)}")


class ErrorHandler:
    """エラーハンドリングの実装"""

    def __init__(self, retry_strategy: Optional[RetryStrategy] = None):
        """
        初期化

        Args:
            retry_strategy: リトライ戦略
        """
        self.retry_strategy = retry_strategy or RetryStrategy()

    async def handle_network_error(
        self,
        url: str,
        status_code: int,
        retry_after: Optional[float] = None
    ) -> None:
        """
        ネットワークエラーの処理

        Args:
            url: リクエスト先URL
            status_code: HTTPステータスコード
            retry_after: リトライまでの待機時間（秒）
        """
        if status_code == 429:  # レート制限
            raise RateLimitError(url, retry_after)
        elif status_code >= 500:  # サーバーエラー
            raise NetworkError(url, status_code)
        else:  # その他のエラー
            logger.error(f"Network error: {status_code} for {url}")

    async def handle_llm_error(
        self,
        message: str,
        raw_response: Any
    ) -> None:
        """
        LLMエラーの処理

        Args:
            message: エラーメッセージ
            raw_response: LLMからの生のレスポンス
        """
        logger.error(f"LLM error: {message}")
        logger.debug(f"Raw response: {raw_response}")
        raise LLMError(message, raw_response)

    async def handle_validation_error(
        self,
        result: Any,
        reason: str
    ) -> None:
        """
        バリデーションエラーの処理

        Args:
            result: 検証対象の結果
            reason: エラーの理由
        """
        logger.error(f"Validation error: {reason}")
        logger.debug(f"Invalid result: {result}")
        raise ValidationError(result, reason) 