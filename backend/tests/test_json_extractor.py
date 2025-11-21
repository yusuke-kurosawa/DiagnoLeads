"""
Tests for JSON Extractor

Comprehensive tests for JSON extraction from AI responses.
"""

import json

import pytest

from app.services.ai.exceptions import AIJSONParseError
from app.services.ai.json_extractor import JSONExtractor


class TestExtractBasic:
    """Tests for basic extract method"""

    def test_extract_plain_json(self):
        """Test extracting plain JSON object"""
        response = '{"key": "value", "number": 42}'
        result = JSONExtractor.extract(response)

        assert result == {"key": "value", "number": 42}

    def test_extract_plain_json_with_whitespace(self):
        """Test extracting JSON with surrounding whitespace"""
        response = '  \n  {"key": "value"}  \n  '
        result = JSONExtractor.extract(response)

        assert result == {"key": "value"}

    def test_extract_empty_string_raises_error(self):
        """Test empty string raises error"""
        with pytest.raises(AIJSONParseError) as exc_info:
            JSONExtractor.extract("")

        assert "Empty response text" in str(exc_info.value)

    def test_extract_whitespace_only_raises_error(self):
        """Test whitespace-only string raises error"""
        with pytest.raises(AIJSONParseError) as exc_info:
            JSONExtractor.extract("   \n   ")

        assert "Empty response text" in str(exc_info.value)

    def test_extract_invalid_json_raises_error(self):
        """Test invalid JSON raises error"""
        response = "This is not JSON at all"

        with pytest.raises(AIJSONParseError) as exc_info:
            JSONExtractor.extract(response)

        assert "Failed to extract JSON" in str(exc_info.value)

    def test_extract_includes_error_preview(self):
        """Test error message includes response preview"""
        response = "Invalid content " * 50  # Long invalid content

        with pytest.raises(AIJSONParseError) as exc_info:
            JSONExtractor.extract(response)

        # Should include first 200 chars
        assert "First 200 chars:" in str(exc_info.value)


class TestExtractFromMarkdownJSON:
    """Tests for extracting from ```json ... ``` blocks"""

    def test_extract_from_markdown_json_block(self):
        """Test extracting from markdown JSON block"""
        response = """Here is the JSON:
```json
{
  "name": "Test",
  "value": 123
}
```
That's it!"""
        result = JSONExtractor.extract(response)

        assert result == {"name": "Test", "value": 123}

    def test_extract_from_markdown_json_with_text_before_after(self):
        """Test extracting with explanatory text"""
        response = """I'll provide the JSON now:

```json
{"status": "success"}
```

Let me know if you need anything else."""
        result = JSONExtractor.extract(response)

        assert result == {"status": "success"}

    def test_extract_from_markdown_json_multiple_blocks_uses_first(self):
        """Test multiple blocks uses first valid one"""
        response = """First block:
```json
{"first": true}
```

Second block:
```json
{"second": true}
```"""
        result = JSONExtractor.extract(response)

        assert result == {"first": True}

    def test_extract_from_markdown_json_complex_object(self):
        """Test extracting complex nested JSON"""
        response = """```json
{
  "assessment": {
    "title": "Lead Qualification",
    "questions": [
      {"id": 1, "text": "What is your role?"},
      {"id": 2, "text": "What is your budget?"}
    ]
  }
}
```"""
        result = JSONExtractor.extract(response)

        assert result["assessment"]["title"] == "Lead Qualification"
        assert len(result["assessment"]["questions"]) == 2


class TestExtractFromMarkdownCode:
    """Tests for extracting from ``` ... ``` blocks"""

    def test_extract_from_markdown_code_block(self):
        """Test extracting from generic markdown code block"""
        response = """```
{"key": "value"}
```"""
        result = JSONExtractor.extract(response)

        assert result == {"key": "value"}

    def test_extract_from_markdown_code_with_language_hint(self):
        """Test extracting from code block with language hint (not json)"""
        # This should still work as it tries both strategies
        response = """```javascript
{"key": "value"}
```"""
        # Will try markdown code strategy
        result = JSONExtractor.extract(response)

        assert result == {"key": "value"}

    def test_extract_from_markdown_code_skips_invalid_blocks(self):
        """Test skips invalid JSON blocks and finds valid one"""
        response = """First block (invalid):
```
This is not JSON
```

Second block (valid):
```
{"valid": true}
```"""
        result = JSONExtractor.extract(response)

        assert result == {"valid": True}


class TestExtractFromJSONObject:
    """Tests for extracting from embedded JSON objects"""

    def test_extract_json_object_from_text(self):
        """Test extracting JSON object from surrounding text"""
        response = 'Here is your data: {"name": "Alice", "age": 30} and that is all.'
        result = JSONExtractor.extract(response)

        assert result == {"name": "Alice", "age": 30}

    def test_extract_json_object_with_nested_braces(self):
        """Test extracting JSON with nested objects"""
        response = """The result is: {"user": {"name": "Bob", "preferences": {"theme": "dark"}}} done"""
        result = JSONExtractor.extract(response)

        assert result["user"]["name"] == "Bob"
        assert result["user"]["preferences"]["theme"] == "dark"

    def test_extract_json_object_with_arrays(self):
        """Test extracting JSON with arrays"""
        response = '{"items": [1, 2, 3], "total": 6}'
        result = JSONExtractor.extract(response)

        assert result["items"] == [1, 2, 3]
        assert result["total"] == 6

    def test_extract_json_object_ignores_text_before(self):
        """Test ignores text before JSON object"""
        response = 'Some explanation text before the JSON object: {"key": "value"}'
        result = JSONExtractor.extract(response)

        assert result == {"key": "value"}

    def test_extract_json_object_ignores_text_after(self):
        """Test ignores text after JSON object"""
        response = '{"key": "value"} followed by some extra text'
        result = JSONExtractor.extract(response)

        assert result == {"key": "value"}


class TestExtractStrategy_Priority:
    """Tests for extraction strategy priority"""

    def test_markdown_json_preferred_over_plain_object(self):
        """Test markdown JSON block is preferred"""
        response = """{"outside": true}

```json
{"inside": true}
```"""
        result = JSONExtractor.extract(response)

        # Should prefer the markdown JSON block
        assert result == {"inside": True}

    def test_markdown_code_fallback(self):
        """Test falls back to markdown code block"""
        response = """```
{"code_block": true}
```

{"plain": true}"""
        result = JSONExtractor.extract(response)

        assert result == {"code_block": True}

    def test_json_object_fallback(self):
        """Test falls back to embedded JSON object"""
        response = 'Text with embedded {"object": true} JSON'
        result = JSONExtractor.extract(response)

        assert result == {"object": True}

    def test_direct_parse_fallback(self):
        """Test falls back to direct parse"""
        response = '{"direct": true}'
        result = JSONExtractor.extract(response)

        assert result == {"direct": True}


class TestExtractFromMarkdownJSONHelper:
    """Tests for _extract_from_markdown_json helper"""

    def test_extract_valid_markdown_json(self):
        """Test extracting from valid markdown JSON block"""
        text = '```json\n{"key": "value"}\n```'
        result = JSONExtractor._extract_from_markdown_json(text)

        assert result == {"key": "value"}

    def test_extract_no_markdown_json_returns_none(self):
        """Test returns None when no markdown JSON block found"""
        text = "Just plain text without JSON blocks"
        result = JSONExtractor._extract_from_markdown_json(text)

        assert result is None

    def test_extract_invalid_json_in_block_raises_error(self):
        """Test invalid JSON in block raises error"""
        text = "```json\nNot valid JSON\n```"

        with pytest.raises(json.JSONDecodeError):
            JSONExtractor._extract_from_markdown_json(text)


class TestExtractFromMarkdownCodeHelper:
    """Tests for _extract_from_markdown_code helper"""

    def test_extract_valid_markdown_code(self):
        """Test extracting from valid markdown code block"""
        text = '```\n{"key": "value"}\n```'
        result = JSONExtractor._extract_from_markdown_code(text)

        assert result == {"key": "value"}

    def test_extract_no_markdown_code_returns_none(self):
        """Test returns None when no markdown code block found"""
        text = "Just plain text"
        result = JSONExtractor._extract_from_markdown_code(text)

        assert result is None

    def test_extract_multiple_blocks_returns_first_valid(self):
        """Test returns first valid JSON from multiple blocks"""
        text = """```
Not JSON
```
```
{"valid": true}
```
```
{"another": true}
```"""
        result = JSONExtractor._extract_from_markdown_code(text)

        assert result == {"valid": True}

    def test_extract_all_invalid_blocks_returns_none(self):
        """Test returns None when all blocks have invalid JSON"""
        text = """```
Not JSON 1
```
```
Not JSON 2
```"""
        result = JSONExtractor._extract_from_markdown_code(text)

        assert result is None


class TestExtractFromJSONObjectHelper:
    """Tests for _extract_from_json_object helper"""

    def test_extract_simple_object(self):
        """Test extracting simple JSON object"""
        text = '{"key": "value"}'
        result = JSONExtractor._extract_from_json_object(text)

        assert result == {"key": "value"}

    def test_extract_no_braces_returns_none(self):
        """Test returns None when no braces found"""
        text = "No JSON here"
        result = JSONExtractor._extract_from_json_object(text)

        assert result is None

    def test_extract_with_text_before_after(self):
        """Test extracting with surrounding text"""
        text = 'Before {"key": "value"} After'
        result = JSONExtractor._extract_from_json_object(text)

        assert result == {"key": "value"}

    def test_extract_nested_objects(self):
        """Test extracting nested JSON objects"""
        text = '{"outer": {"inner": {"deep": "value"}}}'
        result = JSONExtractor._extract_from_json_object(text)

        assert result["outer"]["inner"]["deep"] == "value"

    def test_extract_with_arrays_containing_objects(self):
        """Test extracting with arrays containing objects"""
        text = '{"items": [{"id": 1}, {"id": 2}]}'
        result = JSONExtractor._extract_from_json_object(text)

        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == 1

    def test_extract_malformed_json_returns_none(self):
        """Test returns None for malformed JSON"""
        text = '{"key": "unclosed'
        result = JSONExtractor._extract_from_json_object(text)

        assert result is None

    def test_extract_unmatched_braces_returns_none(self):
        """Test returns None when braces don't match"""
        text = '{"key": "value"'  # Missing closing brace
        result = JSONExtractor._extract_from_json_object(text)

        assert result is None


class TestExtractRealWorldScenarios:
    """Tests for real-world AI response scenarios"""

    def test_extract_claude_response_with_explanation(self):
        """Test typical Claude response format"""
        response = """I'll create the assessment JSON for you:

```json
{
  "title": "B2B SaaS Lead Qualification",
  "description": "Assess potential customers",
  "questions": [
    {
      "id": 1,
      "text": "What is your company size?",
      "options": [
        {"text": "1-10 employees", "points": 1},
        {"text": "11-50 employees", "points": 3},
        {"text": "50+ employees", "points": 5}
      ]
    }
  ]
}
```

This assessment will help identify qualified leads."""
        result = JSONExtractor.extract(response)

        assert result["title"] == "B2B SaaS Lead Qualification"
        assert len(result["questions"]) == 1
        assert len(result["questions"][0]["options"]) == 3

    def test_extract_response_with_markdown_formatting(self):
        """Test response with markdown formatting"""
        response = """# Assessment JSON

Here's the generated assessment:

```json
{"title": "Marketing Assessment", "version": 2}
```

## Notes
- Version 2 includes new features
- Compatible with all browsers"""
        result = JSONExtractor.extract(response)

        assert result == {"title": "Marketing Assessment", "version": 2}

    def test_extract_response_with_mixed_code_blocks(self):
        """Test response with multiple code blocks of different types"""
        response = """Here's some TypeScript:
```typescript
const data = { foo: "bar" };
```

And here's the JSON you requested:
```json
{"actual": "data"}
```"""
        result = JSONExtractor.extract(response)

        assert result == {"actual": "data"}

    def test_extract_inline_json_no_markdown(self):
        """Test extracting inline JSON without markdown"""
        response = 'The generated data is: {"status": "complete", "confidence": 0.95}'
        result = JSONExtractor.extract(response)

        assert result["status"] == "complete"
        assert result["confidence"] == 0.95
