"""
Tests for AI Service Exceptions

Tests the custom exception hierarchy.
"""

import pytest
from app.services.ai.exceptions import (
    AIServiceError,
    AIAPIError,
    AIRateLimitError,
    AIValidationError,
    AIJSONParseError,
    AIPromptInjectionError,
)


class TestAIExceptions:
    """Test cases for AI exception classes"""

    def test_base_exception(self):
        """Test base AIServiceError"""
        error = AIServiceError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.original_error is None

    def test_base_exception_with_original(self):
        """Test AIServiceError with original exception"""
        original = ValueError("Original error")
        error = AIServiceError("Wrapped error", original_error=original)
        assert error.message == "Wrapped error"
        assert error.original_error == original

    def test_api_error(self):
        """Test AIAPIError"""
        error = AIAPIError("API call failed")
        assert isinstance(error, AIServiceError)
        assert str(error) == "API call failed"

    def test_rate_limit_error(self):
        """Test AIRateLimitError"""
        error = AIRateLimitError("Rate limit exceeded", retry_after=60)
        assert isinstance(error, AIServiceError)
        assert error.retry_after == 60

    def test_rate_limit_error_default(self):
        """Test AIRateLimitError with default message"""
        error = AIRateLimitError()
        assert "Rate limit exceeded" in str(error)
        assert error.retry_after is None

    def test_validation_error(self):
        """Test AIValidationError"""
        error = AIValidationError("Validation failed")
        assert isinstance(error, AIServiceError)
        assert "Validation failed" in str(error)

    def test_json_parse_error(self):
        """Test AIJSONParseError"""
        error = AIJSONParseError("Invalid JSON")
        assert isinstance(error, AIServiceError)
        assert "Invalid JSON" in str(error)

    def test_prompt_injection_error(self):
        """Test AIPromptInjectionError"""
        error = AIPromptInjectionError("Suspicious input detected")
        assert isinstance(error, AIServiceError)
        assert "Suspicious input" in str(error)

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from AIServiceError"""
        exceptions = [
            AIAPIError("test"),
            AIRateLimitError("test"),
            AIValidationError("test"),
            AIJSONParseError("test"),
            AIPromptInjectionError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AIServiceError)
            assert isinstance(exc, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching exceptions"""
        with pytest.raises(AIAPIError) as exc_info:
            raise AIAPIError("Test error")

        assert "Test error" in str(exc_info.value)

    def test_catch_as_base_exception(self):
        """Test catching specific exceptions as base AIServiceError"""
        try:
            raise AIRateLimitError("Rate limit hit")
        except AIServiceError as e:
            assert isinstance(e, AIRateLimitError)
            assert "Rate limit hit" in str(e)

    def test_exception_with_nested_original(self):
        """Test exception wrapping chain"""
        original = ConnectionError("Network failed")
        wrapped = AIAPIError("API unreachable", original_error=original)

        assert wrapped.original_error == original
        assert isinstance(wrapped.original_error, ConnectionError)
