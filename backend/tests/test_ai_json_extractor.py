"""
Tests for AI JSON Extractor

Tests the robust JSON extraction logic.
"""

import pytest
import json
from app.services.ai.json_extractor import JSONExtractor
from app.services.ai.exceptions import AIJSONParseError


class TestJSONExtractor:
    """Test cases for JSONExtractor"""

    def test_extract_from_markdown_json(self):
        """Test extraction from markdown JSON block"""
        text = """Here is the result:
```json
{"title": "Test Assessment", "description": "A test", "questions": []}
```
Done!"""

        result = JSONExtractor.extract(text)

        assert result["title"] == "Test Assessment"
        assert result["description"] == "A test"
        assert isinstance(result["questions"], list)

    def test_extract_from_markdown_code(self):
        """Test extraction from generic markdown code block"""
        text = """Result:
```
{"status": "success", "data": {"id": 123}}
```
"""

        result = JSONExtractor.extract(text)

        assert result["status"] == "success"
        assert result["data"]["id"] == 123

    def test_extract_from_json_object(self):
        """Test extraction of embedded JSON object"""
        text = 'Some text {"name": "John", "age": 30} more text'

        result = JSONExtractor.extract(text)

        assert result["name"] == "John"
        assert result["age"] == 30

    def test_extract_from_raw_json(self):
        """Test extraction from raw JSON string"""
        text = '{"type": "raw", "valid": true}'

        result = JSONExtractor.extract(text)

        assert result["type"] == "raw"
        assert result["valid"] is True

    def test_extract_nested_json(self):
        """Test extraction of nested JSON structure"""
        text = """```json
{
  "outer": {
    "inner": {
      "value": "nested"
    }
  }
}
```"""

        result = JSONExtractor.extract(text)

        assert result["outer"]["inner"]["value"] == "nested"

    def test_extract_empty_response_fails(self):
        """Test that empty response raises error"""
        with pytest.raises(AIJSONParseError, match="Empty response"):
            JSONExtractor.extract("")

    def test_extract_invalid_json_fails(self):
        """Test that invalid JSON raises error"""
        text = "This is not JSON at all"

        with pytest.raises(AIJSONParseError):
            JSONExtractor.extract(text)

    def test_extract_multiple_code_blocks_uses_first_valid(self):
        """Test that first valid JSON from multiple blocks is used"""
        text = """First block:
```
invalid json here
```
Second block:
```json
{"valid": true, "id": 1}
```
Third block:
```
{"another": "json"}
```"""

        result = JSONExtractor.extract(text)

        # Should use the first valid JSON (second block)
        assert result["valid"] is True
        assert result["id"] == 1

    def test_extract_with_unicode(self):
        """Test extraction with unicode characters"""
        text = """```json
{"message": "日本語テスト", "emoji": "🎉"}
```"""

        result = JSONExtractor.extract(text)

        assert result["message"] == "日本語テスト"
        assert result["emoji"] == "🎉"

    def test_extract_with_escaped_characters(self):
        """Test extraction with escaped characters"""
        text = r'```json
{"text": "Line 1\nLine 2", "quote": "He said \"hello\""}
```'

        result = JSONExtractor.extract(text)

        assert "Line 1" in result["text"]
        assert "Line 2" in result["text"]
        assert '"' in result["quote"]
