"""
Exceptions モジュールの単体テスト
重要な例外処理の品質保証のための適切なテスト
"""

from app.a2a_prototype.exceptions import (
    A2AProtocolError,
    GeminiA2AError,
    GeminiAPIError,
    GeminiConfigError,
)


class TestGeminiA2AError:
    """GeminiA2AError ベース例外のテスト"""

    def test_create_with_message(self):
        """メッセージ付きで例外を作成"""
        error = GeminiA2AError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)

    def test_create_without_message(self):
        """メッセージなしで例外を作成"""
        error = GeminiA2AError()
        assert str(error) == ""


class TestGeminiConfigError:
    """GeminiConfigError 例外のテスト"""

    def test_create_with_message(self):
        """メッセージ付きで例外を作成"""
        error = GeminiConfigError("config error")
        assert str(error) == "config error"
        assert isinstance(error, GeminiA2AError)
        assert isinstance(error, Exception)

    def test_inheritance_hierarchy(self):
        """継承階層の確認"""
        error = GeminiConfigError("test")
        assert isinstance(error, GeminiA2AError)


class TestGeminiAPIError:
    """GeminiAPIError 例外のテスト"""

    def test_create_with_message(self):
        """メッセージ付きで例外を作成"""
        error = GeminiAPIError("api error")
        assert str(error) == "api error"
        assert isinstance(error, GeminiA2AError)
        assert isinstance(error, Exception)

    def test_inheritance_hierarchy(self):
        """継承階層の確認"""
        error = GeminiAPIError("test")
        assert isinstance(error, GeminiA2AError)


class TestA2AProtocolError:
    """A2AProtocolError 例外のテスト"""

    def test_create_with_message(self):
        """メッセージ付きで例外を作成"""
        error = A2AProtocolError("protocol error")
        assert str(error) == "protocol error"
        assert isinstance(error, GeminiA2AError)
        assert isinstance(error, Exception)

    def test_inheritance_hierarchy(self):
        """継承階層の確認"""
        error = A2AProtocolError("test")
        assert isinstance(error, GeminiA2AError)


class TestExceptionUsage:
    """例外の実際の使用パターンテスト"""

    def test_raise_and_catch_base_error(self):
        """GeminiA2AErrorの発生と捕捉"""
        try:
            raise GeminiA2AError("base error")
        except GeminiA2AError as e:
            assert str(e) == "base error"

    def test_raise_and_catch_config_error(self):
        """GeminiConfigErrorの発生と捕捉"""
        try:
            raise GeminiConfigError("config error")
        except GeminiA2AError as e:  # 基底クラスでキャッチ
            assert str(e) == "config error"

    def test_raise_and_catch_api_error(self):
        """GeminiAPIErrorの発生と捕捉"""
        try:
            raise GeminiAPIError("api error")
        except GeminiA2AError as e:  # 基底クラスでキャッチ
            assert str(e) == "api error"

    def test_raise_and_catch_protocol_error(self):
        """A2AProtocolErrorの発生と捕捉"""
        try:
            raise A2AProtocolError("protocol error")
        except GeminiA2AError as e:  # 基底クラスでキャッチ
            assert str(e) == "protocol error"
