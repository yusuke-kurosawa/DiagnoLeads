"""
JSON Extractor

Robust JSON extraction from various response formats.
"""

import json
import re
from typing import Dict, Any, Optional
import logging

from .exceptions import AIJSONParseError

logger = logging.getLogger(__name__)


class JSONExtractor:
    """Extract and parse JSON from various response formats"""

    @staticmethod
    def extract(response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from response text with multiple fallback strategies.

        Args:
            response_text: Raw response text from AI

        Returns:
            Parsed JSON dictionary

        Raises:
            AIJSONParseError: If JSON extraction fails
        """
        if not response_text or not response_text.strip():
            raise AIJSONParseError("Empty response text")

        # Strategy 1: Try markdown JSON code block (```json ... ```)
        try:
            extracted = JSONExtractor._extract_from_markdown_json(response_text)
            if extracted:
                logger.debug("JSON extracted using markdown strategy")
                return extracted
        except Exception as e:
            logger.debug(f"Markdown JSON extraction failed: {e}")

        # Strategy 2: Try markdown code block (``` ... ```)
        try:
            extracted = JSONExtractor._extract_from_markdown_code(response_text)
            if extracted:
                logger.debug("JSON extracted using markdown code strategy")
                return extracted
        except Exception as e:
            logger.debug(f"Markdown code extraction failed: {e}")

        # Strategy 3: Try to find JSON object directly (first { ... })
        try:
            extracted = JSONExtractor._extract_from_json_object(response_text)
            if extracted:
                logger.debug("JSON extracted using JSON object strategy")
                return extracted
        except Exception as e:
            logger.debug(f"JSON object extraction failed: {e}")

        # Strategy 4: Try to parse entire response as JSON
        try:
            extracted = json.loads(response_text.strip())
            logger.debug("JSON extracted using direct parse strategy")
            return extracted
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parse failed: {e}")

        # All strategies failed
        raise AIJSONParseError(
            f"Failed to extract JSON from response. First 200 chars: {response_text[:200]}"
        )

    @staticmethod
    def _extract_from_markdown_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from ```json ... ``` markdown block"""
        pattern = r"```json\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        if matches:
            # Use the first match
            json_text = matches[0].strip()
            return json.loads(json_text)
        return None

    @staticmethod
    def _extract_from_markdown_code(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from ``` ... ``` markdown block"""
        pattern = r"```\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        if matches:
            # Try each match until we find valid JSON
            for match in matches:
                try:
                    json_text = match.strip()
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    continue
        return None

    @staticmethod
    def _extract_from_json_object(text: str) -> Optional[Dict[str, Any]]:
        """Extract first JSON object from text"""
        # Find the first { and matching }
        start = text.find("{")
        if start == -1:
            return None

        # Count braces to find matching closing brace
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    # Found matching closing brace
                    json_text = text[start : i + 1]
                    try:
                        return json.loads(json_text)
                    except json.JSONDecodeError:
                        return None
        return None
