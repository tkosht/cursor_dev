"""
JSON parsing utilities for LLM responses
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def parse_llm_json_response(response: str) -> dict[str, Any]:
    """
    Parse JSON from LLM response

    Handles various formats:
    - Plain JSON
    - JSON wrapped in ```json blocks
    - JSON wrapped in ``` blocks
    - JSON with surrounding text

    Args:
        response: LLM response string

    Returns:
        Parsed JSON as dictionary

    Raises:
        ValueError: If JSON parsing fails
    """
    if not response:
        return {}

    # Try different extraction methods
    extractors = [
        _extract_json_block,
        _extract_code_block,
        _extract_curly_braces,
        _extract_plain_json,
    ]

    for extractor in extractors:
        try:
            json_str = extractor(response)
            if json_str:
                return safe_json_loads(json_str)
        except Exception as e:
            logger.debug(f"Extractor {extractor.__name__} failed: {e}")
            continue

    # If all extractors fail, try one more time with cleaned response
    cleaned = _clean_response(response)
    try:
        return safe_json_loads(cleaned)
    except Exception as e:
        logger.error(f"Failed to parse JSON from response: {e}")
        logger.debug(f"Response: {response[:500]}...")
        raise ValueError(f"Failed to parse JSON: {e}") from e


def safe_json_loads(json_str: str) -> dict[str, Any]:
    """
    Safely load JSON with error handling

    Args:
        json_str: JSON string

    Returns:
        Parsed JSON as dictionary
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common issues
        fixed = _fix_common_json_issues(json_str)
        return json.loads(fixed)


def _extract_json_block(response: str) -> str | None:
    """Extract JSON from ```json blocks"""
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    return matches[0] if matches else None


def _extract_code_block(response: str) -> str | None:
    """Extract JSON from ``` blocks"""
    pattern = r"```\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)

    for match in matches:
        # Check if it looks like JSON
        if match.strip().startswith("{") or match.strip().startswith("["):
            return match

    return None


def _extract_curly_braces(response: str) -> str | None:
    """Extract content between first { and last }"""
    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1 and end > start:
        return response[start : end + 1]

    # Try with square brackets for arrays
    start = response.find("[")
    end = response.rfind("]")

    if start != -1 and end != -1 and end > start:
        return response[start : end + 1]

    return None


def _extract_plain_json(response: str) -> str | None:
    """Extract plain JSON from response"""
    # Remove common prefixes/suffixes
    lines = response.strip().split("\n")

    # Find lines that look like JSON start/end
    json_lines = []
    in_json = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            in_json = True

        if in_json:
            json_lines.append(line)

        if stripped.endswith("}") or stripped.endswith("]"):
            if in_json:
                break

    return "\n".join(json_lines) if json_lines else None


def _clean_response(response: str) -> str:
    """Clean response for JSON parsing"""
    # Remove common LLM response patterns
    patterns_to_remove = [
        r"Here is the JSON.*?:",
        r"```json",
        r"```",
        r"Response:",
        r"Output:",
        r"Result:",
        r"JSON:",
    ]

    cleaned = response
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def _fix_common_json_issues(json_str: str) -> str:
    """Fix common JSON formatting issues"""
    # Replace single quotes with double quotes
    fixed = json_str.replace("'", '"')

    # Fix trailing commas
    fixed = re.sub(r",\s*}", "}", fixed)
    fixed = re.sub(r",\s*]", "]", fixed)

    # Fix unquoted keys (simple cases)
    fixed = re.sub(r"(\w+):", r'"\1":', fixed)

    # Fix Python-style booleans and None
    fixed = fixed.replace("True", "true")
    fixed = fixed.replace("False", "false")
    fixed = fixed.replace("None", "null")

    return fixed
