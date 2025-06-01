"""
カスタム例外クラス定義

Gemini A2A エージェント関連の例外クラス
"""


class GeminiA2AError(Exception):
    """Gemini A2A エージェント関連のベースエラー"""

    pass


class GeminiConfigError(GeminiA2AError):
    """Gemini設定関連のエラー"""

    pass


class GeminiAPIError(GeminiA2AError):
    """Gemini API通信関連のエラー"""

    pass


class A2AProtocolError(GeminiA2AError):
    """A2Aプロトコル関連のエラー"""

    pass
