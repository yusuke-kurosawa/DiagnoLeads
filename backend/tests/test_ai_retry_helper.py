"""
Tests for AI Retry Helper

Comprehensive tests for retry logic with exponential backoff.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import APIConnectionError, APIError, APITimeoutError, RateLimitError

from app.services.ai.exceptions import AIAPIError, AIRateLimitError
from app.services.ai.retry_helper import retry_with_backoff


@pytest.fixture
def mock_response():
    """Create mock httpx Response"""
    response = MagicMock()
    response.status_code = 429
    response.headers = {}
    return response


@pytest.fixture
def mock_request():
    """Create mock httpx Request"""
    request = MagicMock()
    request.method = "POST"
    request.url = "https://api.anthropic.com/v1/messages"
    return request


@pytest.fixture
def rate_limit_error(mock_response):
    """Create RateLimitError with proper arguments"""
    return RateLimitError("Rate limit exceeded", response=mock_response, body=None)


@pytest.fixture
def connection_error(mock_request):
    """Create APIConnectionError with proper arguments"""
    return APIConnectionError(message="Connection failed", request=mock_request)


@pytest.fixture
def timeout_error(mock_request):
    """Create APITimeoutError with proper arguments"""
    return APITimeoutError(request=mock_request)


@pytest.fixture
def api_error(mock_request):
    """Create APIError with proper arguments"""
    return APIError("Invalid API key", request=mock_request, body=None)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff function"""

    @pytest.mark.asyncio
    async def test_successful_on_first_attempt(self):
        """Test function succeeds on first attempt"""
        async_func = AsyncMock(return_value="success")

        result = await retry_with_backoff(async_func, max_retries=3)

        assert result == "success"
        async_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_after_retry(self, rate_limit_error):
        """Test function succeeds after one retry"""
        async_func = AsyncMock(
            side_effect=[rate_limit_error, "success"]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(async_func, max_retries=3, initial_delay=0.1)

        assert result == "success"
        assert async_func.call_count == 2

    @pytest.mark.asyncio
    async def test_rate_limit_error_after_max_retries(self, rate_limit_error):
        """Test raises AIRateLimitError after max retries"""
        async_func = AsyncMock(
            side_effect=rate_limit_error
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(AIRateLimitError) as exc_info:
                await retry_with_backoff(async_func, max_retries=2, initial_delay=0.1)

        assert "Rate limit exceeded after 2 retries" in str(exc_info.value)
        assert async_func.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_connection_error_retry(self, connection_error):
        """Test retries on API connection error"""
        async_func = AsyncMock(
            side_effect=[connection_error, "success"]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(async_func, max_retries=3, initial_delay=0.1)

        assert result == "success"
        assert async_func.call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_error_retry(self, timeout_error):
        """Test retries on API timeout error"""
        async_func = AsyncMock(
            side_effect=[timeout_error, "success"]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(async_func, max_retries=3, initial_delay=0.1)

        assert result == "success"
        assert async_func.call_count == 2

    @pytest.mark.asyncio
    async def test_connection_error_max_retries(self, connection_error):
        """Test raises AIAPIError after max connection retries"""
        async_func = AsyncMock(
            side_effect=connection_error
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(AIAPIError) as exc_info:
                await retry_with_backoff(async_func, max_retries=2, initial_delay=0.1)

        assert "API connection failed after 2 retries" in str(exc_info.value)
        assert async_func.call_count == 3

    @pytest.mark.asyncio
    async def test_non_retryable_api_error(self, api_error):
        """Test immediately raises on non-retryable API error"""
        async_func = AsyncMock(
            side_effect=api_error
        )

        with pytest.raises(AIAPIError) as exc_info:
            await retry_with_backoff(async_func, max_retries=3)

        assert "API error" in str(exc_info.value)
        async_func.assert_called_once()  # Should not retry

    @pytest.mark.asyncio
    async def test_unexpected_error(self):
        """Test handles unexpected errors"""
        async_func = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )

        with pytest.raises(AIAPIError) as exc_info:
            await retry_with_backoff(async_func, max_retries=3)

        assert "Unexpected error" in str(exc_info.value)
        async_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, mock_response):
        """Test exponential backoff delay calculation"""
        # Create multiple rate limit errors
        error1 = RateLimitError("Rate limit", response=mock_response, body=None)
        error2 = RateLimitError("Rate limit", response=mock_response, body=None)

        async_func = AsyncMock(
            side_effect=[error1, error2, "success"]
        )

        sleep_calls = []

        async def mock_sleep(delay):
            sleep_calls.append(delay)

        with patch("asyncio.sleep", side_effect=mock_sleep):
            result = await retry_with_backoff(
                async_func,
                max_retries=3,
                initial_delay=1.0,
                backoff_factor=2.0,
            )

        assert result == "success"
        assert len(sleep_calls) == 2
        # Delay is multiplied AFTER first failure, so first sleep uses multiplied delay
        assert sleep_calls[0] == 2.0  # First retry (1.0 * 2.0)
        assert sleep_calls[1] == 4.0  # Second retry (2.0 * 2.0)

    @pytest.mark.asyncio
    async def test_custom_backoff_factor(self, mock_response):
        """Test custom backoff factor"""
        # Create multiple rate limit errors
        error1 = RateLimitError("Rate limit", response=mock_response, body=None)
        error2 = RateLimitError("Rate limit", response=mock_response, body=None)

        async_func = AsyncMock(
            side_effect=[error1, error2, "success"]
        )

        sleep_calls = []

        async def mock_sleep(delay):
            sleep_calls.append(delay)

        with patch("asyncio.sleep", side_effect=mock_sleep):
            result = await retry_with_backoff(
                async_func,
                max_retries=3,
                initial_delay=1.0,
                backoff_factor=3.0,  # Triple each time
            )

        assert result == "success"
        # Delay is multiplied AFTER first failure
        assert sleep_calls[0] == 3.0  # First retry (1.0 * 3.0)
        assert sleep_calls[1] == 9.0  # Second retry (3.0 * 3.0)

    @pytest.mark.asyncio
    async def test_function_with_args(self):
        """Test retry with function arguments"""
        async_func = AsyncMock(return_value="success")

        # Pass all retry parameters first, then function args
        result = await retry_with_backoff(
            async_func,
            3,  # max_retries
            1.0,  # initial_delay
            2.0,  # backoff_factor
            "arg1",  # args for async_func
            "arg2",
        )

        assert result == "success"
        async_func.assert_called_once_with("arg1", "arg2")

    @pytest.mark.asyncio
    async def test_function_with_kwargs(self):
        """Test retry with function keyword arguments"""
        async_func = AsyncMock(return_value="success")

        result = await retry_with_backoff(
            async_func,
            max_retries=3,
            key1="value1",
            key2="value2",
        )

        assert result == "success"
        async_func.assert_called_once_with(key1="value1", key2="value2")

    @pytest.mark.asyncio
    async def test_zero_max_retries(self, rate_limit_error):
        """Test with zero max retries"""
        async_func = AsyncMock(
            side_effect=rate_limit_error
        )

        with pytest.raises(AIRateLimitError):
            await retry_with_backoff(async_func, max_retries=0, initial_delay=0.1)

        async_func.assert_called_once()  # Only initial attempt

    @pytest.mark.asyncio
    async def test_rate_limit_with_retry_after(self, mock_response):
        """Test rate limit error with retry_after attribute"""
        error = RateLimitError("Rate limit", response=mock_response, body=None)
        error.retry_after = 60

        async_func = AsyncMock(side_effect=error)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(AIRateLimitError):
                await retry_with_backoff(async_func, max_retries=0, initial_delay=0.1)

        # Should capture retry_after from original error
        assert async_func.call_count == 1
