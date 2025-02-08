"""カスタム例外クラスを定義するモジュール。"""


class BaseError(Exception):
    """基本例外クラス。"""
    pass


class ValidationError(BaseError):
    """バリデーションエラー。"""
    pass


class GeminiAPIError(BaseError):
    """Gemini API関連のエラー。"""
    pass


class ServiceUnavailable(BaseError):
    """サービス利用不可エラー。"""
    pass


class Neo4jError(BaseError):
    """Neo4jデータベース関連のエラー。"""
    pass


class DatabaseError(BaseError):
    """データベース操作関連のエラー。"""
    pass


class TransactionError(BaseError):
    """トランザクション関連のエラー。"""
    pass


class MarketCrawlerError(BaseError):
    """市場クローラー関連のエラー。"""
    pass


class ContentFetchError(BaseError):
    """コンテンツ取得関連のエラー。"""
    pass


class ContentParseError(BaseError):
    """コンテンツ解析関連のエラー。"""
    pass


class TransientError(BaseError):
    """一時的なエラー。"""
    pass


class ConnectionError(BaseError):
    """接続関連のエラー。"""
    pass


class MarketAnalysisError(BaseError):
    """市場分析関連のエラー。"""
    pass


class GeminiError(BaseError):
    """Gemini APIエラー。"""
    pass 