"""
Retry Helper

Provides retry logic with exponential backoff for API calls.
"""

import asyncio
import logging
from typing import Callable, TypeVar, Awaitable

from anthropic import (
    APIError,
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)

from .exceptions import AIAPIError, AIRateLimitError

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from func

    Raises:
        AIRateLimitError: If rate limit is hit after all retries
        AIAPIError: If API error occurs after all retries
    """
    last_exception = None
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(
                    f"Retry attempt {attempt}/{max_retries} after {delay}s delay"
                )
                await asyncio.sleep(delay)

            result = await func(*args, **kwargs)
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt}")
            return result

        except RateLimitError as e:
            last_exception = e
            logger.warning(
                f"Rate limit hit on attempt {attempt + 1}/{max_retries + 1}: {e}"
            )
            if attempt == max_retries:
                raise AIRateLimitError(
                    f"Rate limit exceeded after {max_retries} retries",
                    retry_after=getattr(e, "retry_after", None),
                )
            delay *= backoff_factor

        except (APIConnectionError, APITimeoutError) as e:
            last_exception = e
            logger.warning(
                f"Connection error on attempt {attempt + 1}/{max_retries + 1}: {e}"
            )
            if attempt == max_retries:
                raise AIAPIError(
                    f"API connection failed after {max_retries} retries",
                    original_error=e,
                )
            delay *= backoff_factor

        except APIError as e:
            # Non-retryable API errors
            logger.error(f"Non-retryable API error: {e}")
            raise AIAPIError(f"API error: {str(e)}", original_error=e)

        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise AIAPIError(f"Unexpected error: {str(e)}", original_error=e)

    # Should not reach here, but just in case
    if last_exception:
        raise AIAPIError(
            f"Max retries ({max_retries}) exceeded",
            original_error=last_exception,
        )
    raise AIAPIError("Unknown error in retry logic")
