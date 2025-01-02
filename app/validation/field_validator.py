"""Field validation utilities."""

import logging
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class FieldValidator:
    """フィールドバリデーションユーティリティ"""

    @staticmethod
    def validate_field(value: Any, field_type: Optional[Type] = None) -> bool:
        """フィールドの値を検証

        Args:
            value: 検証対象の値
            field_type: 期待される型（オプション）

        Returns:
            bool: 検証結果
        """
        if value is None:
            return False

        if field_type and not isinstance(value, field_type):
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, (list, dict)):
            return bool(value)

        return True

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        field_types: Optional[Dict[str, Type]] = None
    ) -> bool:
        """必須フィールドを検証

        Args:
            data: 検証対象のデータ
            required_fields: 必要なフィールドのリスト
            field_types: フィールドの型定義（オプション）

        Returns:
            bool: 検証結果
        """
        if not data:
            return False

        field_types = field_types or {}

        for field in required_fields:
            if field not in data:
                logger.debug(f"必須フィールドが存在しません: {field}")
                return False

            field_type = field_types.get(field)
            if not FieldValidator.validate_field(data[field], field_type):
                logger.debug(f"フィールドの値が無効です: {field}")
                return False

        return True

    @staticmethod
    def get_missing_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        field_types: Optional[Dict[str, Type]] = None
    ) -> List[str]:
        """不足しているフィールドを取得

        Args:
            data: 検証対象のデータ
            required_fields: 必要なフィールドのリスト
            field_types: フィールドの型定義（オプション）

        Returns:
            List[str]: 不足しているフィールドのリスト
        """
        field_types = field_types or {}
        missing = []

        for field in required_fields:
            if field not in data:
                missing.append(field)
                continue

            field_type = field_types.get(field)
            if not FieldValidator.validate_field(data[field], field_type):
                missing.append(field)

        return missing 