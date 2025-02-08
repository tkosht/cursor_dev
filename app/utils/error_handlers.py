"""エラーハンドリングユーティリティモジュール。"""

import functools
import logging
import time
from typing import Any, Callable, Optional, Type, Union

from app.exceptions import ValidationError

logger = logging.getLogger(__name__)


def retry_on_error(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exceptions: Optional[Union[Type[Exception], tuple]] = None
) -> Callable:
    """
    一時的なエラーが発生した場合にリトライするデコレータ。

    Args:
        max_retries (int): 最大リトライ回数
        retry_delay (float): リトライ間隔（秒）
        exceptions (Optional[Union[Type[Exception], tuple]]): 
            リトライ対象の例外クラス。Noneの場合は全ての例外をリトライ。

    Returns:
        Callable: デコレータ関数
    """
    if exceptions is None:
        exceptions = (Exception,)
    elif not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(
                            f"リトライ {attempt + 1}/{max_retries} "
                            f"エラー: {str(e)}, {wait_time}秒後に再試行"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"最大リトライ回数({max_retries})を超過: {str(e)}"
                        )
                        raise
            return last_error
        return wrapper
    return decorator


def validate_input(validator: Callable) -> Callable:
    """
    入力値を検証するデコレータ。

    Args:
        validator (Callable): 検証関数

    Returns:
        Callable: デコレータ関数

    Raises:
        ValidationError: 検証に失敗した場合
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not validator(*args):
                error_msg = f"入力値の検証に失敗しました: {func.__name__}"
                logger.error(error_msg)
                raise ValidationError(error_msg)
            return func(*args, **kwargs)
        return wrapper
    return decorator 