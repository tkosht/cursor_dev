"""LLM based page parser module."""
import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMParser:
    """Parser that uses LLM to extract information from HTML content."""

    def __init__(self, api_key: str) -> None:
        """Initialize parser.

        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)

    def _create_prompt(
        self, html_content: str, page_type: str, expected_fields: Dict[str, str]
    ) -> str:
        """Create prompt for LLM.

        Args:
            html_content: HTML content to parse
            page_type: Type of page (company_info, financial_info, etc.)
            expected_fields: Dictionary of field names and their descriptions

        Returns:
            Formatted prompt string
        """
        fields_str = "\n".join([f"- {k}: {v}" for k, v in expected_fields.items()])

        return f"""
以下のHTML内容から情報を抽出してください。
���ージタイプ: {page_type}

抽出する項目:
{fields_str}

出力形式: JSON
期待される構造:
{{
    "extracted_data": {{
        "field_name": "抽出された値",
        ...
    }},
    "confidence": 0.0-1.0  // 抽出の確信度
}}

HTML内容:
{html_content}
"""

    def parse(
        self, html_content: str, page_type: str, expected_fields: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Parse HTML content using LLM.

        Args:
            html_content: HTML content to parse
            page_type: Type of page (company_info, financial_info, etc.)
            expected_fields: Dictionary of field names and their descriptions

        Returns:
            Parsed data or None if parsing failed
        """
        try:
            prompt = self._create_prompt(html_content, page_type, expected_fields)

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはHTMLパーサーです。指定されたHTML"
                        "から必要な情報を抽出し、構造化されたデータとして"
                        "返してください。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )

            result = response.choices[0].message.content
            parsed_data = json.loads(result)

            # 結果の検証
            if not self._validate_parsed_data(parsed_data, expected_fields):
                logger.warning("Parsed data validation failed")
                return None

            return parsed_data

        except Exception as e:
            logger.error(f"Parsing failed: {str(e)}")
            return None

    def _validate_parsed_data(
        self, parsed_data: Dict[str, Any], expected_fields: Dict[str, str]
    ) -> bool:
        """Validate parsed data.

        Args:
            parsed_data: Parsed data to validate
            expected_fields: Dictionary of expected fields

        Returns:
            True if validation passed, False otherwise
        """
        try:
            if "extracted_data" not in parsed_data:
                return False

            if "confidence" not in parsed_data:
                return False

            extracted_data = parsed_data["extracted_data"]
            confidence = float(parsed_data["confidence"])

            # 信頼度のチェック
            if not (0.0 <= confidence <= 1.0):
                return False

            # 必須フィールドの存在チェック
            for field in expected_fields:
                if field not in extracted_data:
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False
