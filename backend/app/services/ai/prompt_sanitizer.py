"""
Prompt Sanitizer

Sanitizes user input to prevent prompt injection attacks.
"""

import re
import logging
from typing import Dict, Any

from .exceptions import AIPromptInjectionError

logger = logging.getLogger(__name__)


class PromptSanitizer:
    """Sanitize user input to prevent prompt injection"""

    # Suspicious patterns that might indicate prompt injection
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
        r"disregard\s+(previous|above|all)",
        r"you\s+are\s+now",
        r"new\s+instructions",
        r"system\s*:",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[INST\]",
        r"\[/INST\]",
    ]

    # Maximum allowed length for various input types
    MAX_TOPIC_LENGTH = 500
    MAX_TEXT_LENGTH = 5000

    @staticmethod
    def sanitize_topic(topic: str) -> str:
        """
        Sanitize assessment topic input.

        Args:
            topic: Raw topic string

        Returns:
            Sanitized topic string

        Raises:
            AIPromptInjectionError: If suspicious patterns detected
        """
        if not topic or not topic.strip():
            raise AIPromptInjectionError("Topic cannot be empty")

        topic = topic.strip()

        # Check length
        if len(topic) > PromptSanitizer.MAX_TOPIC_LENGTH:
            raise AIPromptInjectionError(
                f"Topic too long (max {PromptSanitizer.MAX_TOPIC_LENGTH} chars)"
            )

        # Check for suspicious patterns
        PromptSanitizer._check_suspicious_patterns(topic, "topic")

        # Remove excessive newlines
        topic = re.sub(r"\n{3,}", "\n\n", topic)

        return topic

    @staticmethod
    def sanitize_text(text: str, max_length: int = None) -> str:
        """
        Sanitize general text input.

        Args:
            text: Raw text string
            max_length: Maximum allowed length (default: MAX_TEXT_LENGTH)

        Returns:
            Sanitized text string

        Raises:
            AIPromptInjectionError: If suspicious patterns detected
        """
        if not text or not text.strip():
            raise AIPromptInjectionError("Text cannot be empty")

        text = text.strip()
        max_len = max_length or PromptSanitizer.MAX_TEXT_LENGTH

        # Check length
        if len(text) > max_len:
            raise AIPromptInjectionError(f"Text too long (max {max_len} chars)")

        # Check for suspicious patterns
        PromptSanitizer._check_suspicious_patterns(text, "text")

        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    @staticmethod
    def sanitize_responses(responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize assessment response data.

        Args:
            responses: Raw response dictionary

        Returns:
            Sanitized response dictionary

        Raises:
            AIPromptInjectionError: If suspicious patterns detected
        """
        if not isinstance(responses, dict):
            raise AIPromptInjectionError("Responses must be a dictionary")

        sanitized = {}
        for key, value in responses.items():
            # Sanitize key
            if not isinstance(key, str):
                key = str(key)
            if len(key) > 100:
                raise AIPromptInjectionError("Response key too long")

            # Sanitize value
            if isinstance(value, str):
                if len(value) > 1000:
                    raise AIPromptInjectionError("Response value too long")
                PromptSanitizer._check_suspicious_patterns(value, "response value")
                sanitized[key] = value.strip()
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = PromptSanitizer.sanitize_responses(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    PromptSanitizer._sanitize_list_item(item) for item in value
                ]
            else:
                logger.warning(f"Unexpected value type in responses: {type(value)}")
                sanitized[key] = str(value)

        return sanitized

    @staticmethod
    def _sanitize_list_item(item: Any) -> Any:
        """Sanitize individual list items"""
        if isinstance(item, str):
            if len(item) > 1000:
                raise AIPromptInjectionError("List item too long")
            PromptSanitizer._check_suspicious_patterns(item, "list item")
            return item.strip()
        elif isinstance(item, (int, float, bool)):
            return item
        elif isinstance(item, dict):
            return PromptSanitizer.sanitize_responses(item)
        else:
            return str(item)

    @staticmethod
    def _check_suspicious_patterns(text: str, field_name: str) -> None:
        """
        Check for suspicious patterns in text.

        Args:
            text: Text to check
            field_name: Name of field for error messages

        Raises:
            AIPromptInjectionError: If suspicious pattern detected
        """
        text_lower = text.lower()

        for pattern in PromptSanitizer.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(
                    f"Suspicious pattern detected in {field_name}: {pattern}"
                )
                raise AIPromptInjectionError(
                    f"Suspicious content detected in {field_name}. Please rephrase your input."
                )
