"""
Unit tests for JSON parsing utilities
"""

from unittest.mock import patch

import pytest
from src.utils.json_parser import (
    _clean_response,
    _extract_code_block,
    _extract_curly_braces,
    _extract_json_block,
    _extract_plain_json,
    _fix_common_json_issues,
    parse_llm_json_response,
    safe_json_loads,
)


class TestParseLLMJsonResponse:
    """Test main parse_llm_json_response function"""

    def test_empty_response(self):
        """Test empty response handling"""
        assert parse_llm_json_response("") == {}
        assert parse_llm_json_response(None) == {}

    def test_plain_json(self):
        """Test parsing plain JSON"""
        response = '{"key": "value", "number": 42}'
        result = parse_llm_json_response(response)
        assert result == {"key": "value", "number": 42}

    def test_json_in_code_block(self):
        """Test parsing JSON in ```json block"""
        response = """Here's the result:
```json
{
    "status": "success",
    "data": {
        "items": [1, 2, 3]
    }
}
```
That's the output."""

        result = parse_llm_json_response(response)
        assert result["status"] == "success"
        assert result["data"]["items"] == [1, 2, 3]

    def test_json_in_plain_code_block(self):
        """Test parsing JSON in plain ``` block"""
        response = """```
{"result": true, "score": 0.95}
```"""

        result = parse_llm_json_response(response)
        assert result["result"] is True
        assert result["score"] == 0.95

    def test_json_with_surrounding_text(self):
        """Test parsing JSON with surrounding text"""
        response = """The analysis result is as follows:
{"analysis": "complete", "confidence": 0.8, "findings": ["a", "b"]}
That concludes the analysis."""

        result = parse_llm_json_response(response)
        assert result["analysis"] == "complete"
        assert result["confidence"] == 0.8
        assert result["findings"] == ["a", "b"]

    def test_array_json(self):
        """Test parsing JSON array"""
        response = '[{"id": 1}, {"id": 2}]'
        result = parse_llm_json_response(response)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_malformed_json_recovery(self):
        """Test recovery from malformed JSON"""
        # Single quotes instead of double quotes
        response = "{'key': 'value'}"
        result = parse_llm_json_response(response)
        assert result["key"] == "value"

    def test_parse_failure(self):
        """Test parsing failure"""
        response = "This is not JSON at all"
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_llm_json_response(response)


class TestSafeJsonLoads:
    """Test safe_json_loads function"""

    def test_valid_json(self):
        """Test loading valid JSON"""
        json_str = '{"valid": true}'
        result = safe_json_loads(json_str)
        assert result["valid"] is True

    def test_json_with_trailing_comma(self):
        """Test fixing trailing comma"""
        json_str = '{"a": 1, "b": 2,}'
        result = safe_json_loads(json_str)
        assert result == {"a": 1, "b": 2}

    def test_json_with_single_quotes(self):
        """Test fixing single quotes"""
        json_str = "{'key': 'value'}"
        result = safe_json_loads(json_str)
        assert result["key"] == "value"

    def test_json_with_python_booleans(self):
        """Test fixing Python-style booleans"""
        json_str = '{"active": True, "deleted": False, "data": None}'
        result = safe_json_loads(json_str)
        assert result["active"] is True
        assert result["deleted"] is False
        assert result["data"] is None


class TestExtractors:
    """Test individual extractor functions"""

    def test_extract_json_block(self):
        """Test extracting from ```json blocks"""
        text = '```json\n{"test": 123}\n```'
        assert _extract_json_block(text) == '{"test": 123}'

        # No json block
        assert _extract_json_block("no json here") is None

    def test_extract_code_block(self):
        """Test extracting from ``` blocks"""
        # JSON-like content
        text = '```\n{"code": true}\n```'
        assert _extract_code_block(text) == '{"code": true}'

        # Array
        text = "```\n[1, 2, 3]\n```"
        assert _extract_code_block(text) == "[1, 2, 3]"

        # Non-JSON code block
        text = "```\nprint('hello')\n```"
        assert _extract_code_block(text) is None

    def test_extract_curly_braces(self):
        """Test extracting between curly braces"""
        # Object
        text = 'Before {"extracted": "value"} after'
        assert _extract_curly_braces(text) == '{"extracted": "value"}'

        # Array
        text = "Before [1, 2, 3] after"
        assert _extract_curly_braces(text) == "[1, 2, 3]"

        # Nested
        text = 'Start {"outer": {"inner": "value"}} end'
        assert _extract_curly_braces(text) == '{"outer": {"inner": "value"}}'

        # No JSON
        assert _extract_curly_braces("no brackets") is None

    def test_extract_plain_json(self):
        """Test extracting plain JSON"""
        text = """Some text
{
    "key": "value",
    "number": 42
}
More text"""

        result = _extract_plain_json(text)
        assert '"key"' in result
        assert '"value"' in result

        # No JSON
        assert _extract_plain_json("just text") is None


class TestHelperFunctions:
    """Test helper functions"""

    def test_clean_response(self):
        """Test response cleaning"""
        response = 'Here is the JSON: ```json\n{"test": 1}\n```'
        cleaned = _clean_response(response)
        assert "Here is the JSON" not in cleaned
        assert "```json" not in cleaned
        assert '{"test": 1}' in cleaned

    def test_fix_common_json_issues(self):
        """Test fixing common JSON issues"""
        # Trailing commas
        assert _fix_common_json_issues('{"a": 1,}') == '{"a": 1}'
        assert _fix_common_json_issues("[1, 2,]") == "[1, 2]"

        # Single quotes
        assert _fix_common_json_issues("{'key': 'val'}") == '{"key": "val"}'

        # Unquoted keys
        assert _fix_common_json_issues('{key: "value"}') == '{"key": "value"}'

        # Python booleans
        assert (
            _fix_common_json_issues('{"t": True, "f": False}')
            == '{"t": true, "f": false}'
        )

        # Python None
        assert _fix_common_json_issues('{"val": None}') == '{"val": null}'


class TestLogging:
    """Test logging behavior"""

    @patch("src.utils.json_parser.logger")
    def test_debug_logging_on_extractor_failure(self, mock_logger):
        """Test debug logging when extractors fail"""
        # Create a response that will fail initial extractors
        response = "Not JSON but has {invalid json}"

        try:
            parse_llm_json_response(response)
        except ValueError:
            pass

        # Check that debug was called for failed extractors
        assert mock_logger.debug.called

    @patch("src.utils.json_parser.logger")
    def test_error_logging_on_final_failure(self, mock_logger):
        """Test error logging on final parsing failure"""
        response = "This will definitely fail"

        try:
            parse_llm_json_response(response)
        except ValueError:
            pass

        # Check that error was logged
        mock_logger.error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
