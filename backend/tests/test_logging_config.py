"""
Tests for Logging Configuration Module

Comprehensive tests for logging setup and logger retrieval.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from app.core.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """Tests for setup_logging function"""

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_default(self, mock_basic_config):
        """Test setup_logging with default parameters"""
        setup_logging()

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO
        assert "%(asctime)s" in call_kwargs["format"]
        assert "%(levelname)s" in call_kwargs["format"]

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_debug_level(self, mock_basic_config):
        """Test setup_logging with DEBUG level"""
        setup_logging(level="DEBUG")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.DEBUG

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_warning_level(self, mock_basic_config):
        """Test setup_logging with WARNING level"""
        setup_logging(level="WARNING")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.WARNING

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_error_level(self, mock_basic_config):
        """Test setup_logging with ERROR level"""
        setup_logging(level="ERROR")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.ERROR

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_critical_level(self, mock_basic_config):
        """Test setup_logging with CRITICAL level"""
        setup_logging(level="CRITICAL")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.CRITICAL

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_lowercase_level(self, mock_basic_config):
        """Test setup_logging handles lowercase level names"""
        setup_logging(level="info")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_invalid_level(self, mock_basic_config):
        """Test setup_logging with invalid level defaults to INFO"""
        setup_logging(level="INVALID")

        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO

    @patch("app.core.logging_config.logging.basicConfig")
    def test_setup_logging_json_format_parameter(self, mock_basic_config):
        """Test setup_logging accepts json_format parameter"""
        # Note: Current implementation doesn't use json_format,
        # but parameter should be accepted without error
        setup_logging(json_format=True)

        mock_basic_config.assert_called_once()


class TestGetLogger:
    """Tests for get_logger function"""

    def test_get_logger_basic(self):
        """Test getting a logger with basic name"""
        logger = get_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_module_name(self):
        """Test getting a logger with module name"""
        logger = get_logger(__name__)

        assert isinstance(logger, logging.Logger)
        assert __name__ in logger.name

    def test_get_logger_with_level_override(self):
        """Test getting a logger with level override"""
        logger = get_logger("test_logger_debug", level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_get_logger_with_warning_level(self):
        """Test getting a logger with WARNING level"""
        logger = get_logger("test_logger_warning", level="WARNING")

        assert logger.level == logging.WARNING

    def test_get_logger_with_error_level(self):
        """Test getting a logger with ERROR level"""
        logger = get_logger("test_logger_error", level="ERROR")

        assert logger.level == logging.ERROR

    def test_get_logger_lowercase_level(self):
        """Test get_logger handles lowercase level names"""
        logger = get_logger("test_logger_lower", level="info")

        assert logger.level == logging.INFO

    def test_get_logger_invalid_level(self):
        """Test get_logger with invalid level defaults to INFO"""
        logger = get_logger("test_logger_invalid", level="INVALID")

        assert logger.level == logging.INFO

    def test_get_logger_without_level(self):
        """Test get_logger without level override uses default"""
        logger = get_logger("test_logger_default")

        # Logger should exist but level not explicitly set
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for same name"""
        logger1 = get_logger("shared_logger")
        logger2 = get_logger("shared_logger")

        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self):
        """Test that different names return different logger instances"""
        logger1 = get_logger("logger_one")
        logger2 = get_logger("logger_two")

        assert logger1 is not logger2
        assert logger1.name != logger2.name
