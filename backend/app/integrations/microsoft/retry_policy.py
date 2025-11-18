"""
Microsoft Graph API リトライポリシー
レート制限、一時的なエラーに対応
"""

import asyncio
from typing import Callable, TypeVar, Any
from functools import wraps
import httpx

T = TypeVar("T")


class RetryPolicy:
    """
    Exponential Backoffでリトライを実行
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
    ):
        """
        Args:
            max_retries: 最大リトライ回数
            initial_delay: 初回遅延時間（秒）
            max_delay: 最大遅延時間（秒）
            exponential_base: 指数バックオフの基数
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def should_retry(self, exception: Exception) -> bool:
        """
        リトライすべきエラーかどうかを判定

        Args:
            exception: 発生した例外

        Returns:
            リトライすべき場合はTrue
        """
        # HTTPステータスエラー
        if isinstance(exception, httpx.HTTPStatusError):
            status_code = exception.response.status_code

            # 429: Too Many Requests (Rate Limit)
            if status_code == 429:
                return True

            # 5xx: Server Errors
            if 500 <= status_code < 600:
                return True

            # 408: Request Timeout
            if status_code == 408:
                return True

        # ネットワークエラー
        if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException)):
            return True

        return False

    def get_retry_after(self, exception: Exception, attempt: int) -> float:
        """
        次のリトライまでの待機時間を計算

        Args:
            exception: 発生した例外
            attempt: リトライ回数（0から開始）

        Returns:
            待機時間（秒）
        """
        # Rate Limitの場合、Retry-Afterヘッダーを確認
        if isinstance(exception, httpx.HTTPStatusError):
            if exception.response.status_code == 429:
                retry_after = exception.response.headers.get("Retry-After")
                if retry_after:
                    try:
                        return float(retry_after)
                    except ValueError:
                        pass

        # Exponential Backoff
        delay = self.initial_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)

    async def execute_with_retry(
        self, func: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """
        関数をリトライロジック付きで実行

        Args:
            func: 実行する非同期関数
            *args: 関数の引数
            **kwargs: 関数のキーワード引数

        Returns:
            関数の戻り値

        Raises:
            最後のリトライで発生した例外
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # リトライすべきでない場合は即座に再送出
                if not self.should_retry(e):
                    raise

                # 最後のリトライの場合も再送出
                if attempt >= self.max_retries:
                    raise

                # 待機時間を計算
                delay = self.get_retry_after(e, attempt)

                print(
                    f"⚠️  Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s due to: {str(e)[:100]}"
                )

                # 待機
                await asyncio.sleep(delay)

        # 到達しないはずだが、念のため
        if last_exception:
            raise last_exception


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
):
    """
    デコレーター: 関数にリトライロジックを追加

    Usage:
        @with_retry(max_retries=3, initial_delay=1.0)
        async def my_api_call():
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            policy = RetryPolicy(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
            )
            return await policy.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator


# デフォルトのリトライポリシー
default_retry_policy = RetryPolicy(
    max_retries=3, initial_delay=1.0, max_delay=60.0, exponential_base=2.0
)
