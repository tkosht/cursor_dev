"""
LLM関連のエラー定義
"""


class LLMError(Exception):
    """LLM関連の基本エラー"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ModelNotFoundError(LLMError):
    """モデルが見つからない場合のエラー"""
    pass 