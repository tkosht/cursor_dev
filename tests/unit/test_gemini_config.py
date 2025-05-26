"""
GeminiConfig クラスの単体テスト
TDD Green フェーズ: 実装後のテスト有効化
"""

import os
from unittest.mock import patch

import pytest

# テスト対象のクラス
from app.a2a_prototype.utils.gemini_config import GeminiConfig


class TestGeminiConfig:
    """GeminiConfig クラスのテスト"""

    def test_create_with_valid_data(self):
        """正常ケース: 有効なデータでGeminiConfigを作成"""
        # Given: 有効な設定データ
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        # When: GeminiConfigを作成
        config = GeminiConfig(**config_data)

        # Then: 期待される値で正確に作成される
        assert config.api_key == "test-api-key-12345678"
        assert config.model == "gemini-2.5-pro"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.safety_settings is None

    def test_create_with_invalid_api_key_empty(self):
        """異常ケース: 空のAPIキー"""
        # Given: 空のAPIキー
        config_data = {
            "api_key": "",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(
            ValueError, match="API key must be a non-empty string"
        ):
            GeminiConfig(**config_data)

    def test_create_with_invalid_api_key_too_short(self):
        """異常ケース: APIキーが短すぎる"""
        # Given: 短すぎるAPIキー
        config_data = {
            "api_key": "short",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(ValueError, match="API key appears to be invalid"):
            GeminiConfig(**config_data)

    def test_create_with_invalid_temperature_below_zero(self):
        """異常ケース: temperatureが0未満"""
        # Given: 無効なtemperature
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": -0.1,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(
            ValueError, match="Temperature must be between 0.0 and 1.0"
        ):
            GeminiConfig(**config_data)

    def test_create_with_invalid_temperature_above_one(self):
        """異常ケース: temperatureが1超過"""
        # Given: 無効なtemperature
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 1.1,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(
            ValueError, match="Temperature must be between 0.0 and 1.0"
        ):
            GeminiConfig(**config_data)

    def test_create_with_invalid_max_tokens_zero(self):
        """異常ケース: max_tokensが0"""
        # Given: 無効なmax_tokens
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 0,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(
            ValueError, match="Max tokens must be between 1 and 8192"
        ):
            GeminiConfig(**config_data)

    def test_create_with_invalid_max_tokens_too_large(self):
        """異常ケース: max_tokensが上限超過"""
        # Given: 無効なmax_tokens
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 10000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(
            ValueError, match="Max tokens must be between 1 and 8192"
        ):
            GeminiConfig(**config_data)

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-api-key-12345678",
            "GEMINI_MODEL": "gemini-2.5-pro",
            "GEMINI_TEMPERATURE": "0.5",
            "GEMINI_MAX_TOKENS": "500",
        },
    )
    def test_from_env_with_all_variables(self):
        """正常ケース: 環境変数からの設定読み込み"""
        # When: 環境変数からGeminiConfigを作成
        config = GeminiConfig.from_env()

        # Then: 環境変数の値が設定される
        assert config.api_key == "test-api-key-12345678"
        assert config.model == "gemini-2.5-pro"
        assert config.temperature == 0.5
        assert config.max_tokens == 500

    def test_from_env_missing_api_key(self):
        """異常ケース: GEMINI_API_KEY環境変数が未設定"""
        # Given: GEMINI_API_KEYが未設定の環境
        with patch.dict(os.environ, {}, clear=True):
            # When & Then: ValueErrorが発生する
            with pytest.raises(
                ValueError,
                match="GEMINI_API_KEY environment variable is required",
            ):
                GeminiConfig.from_env()

    def test_to_generation_config(self):
        """正常ケース: GenerationConfig形式への変換"""
        # Given: 有効なGeminiConfig
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        config = GeminiConfig(**config_data)

        # When: GenerationConfig形式に変換
        result = config.to_generation_config()

        # Then: 期待される形式で変換される
        expected = {
            "temperature": 0.7,
            "max_output_tokens": 1000,
        }
        assert result == expected

    def test_get_masked_api_key(self):
        """正常ケース: APIキーのマスキング"""
        # Given: 有効なGeminiConfig
        config_data = {
            "api_key": "test-api-key-12345678",  # 21文字
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        config = GeminiConfig(**config_data)

        # When: マスキングされたAPIキーを取得
        masked_key = config.get_masked_api_key()

        # Then: 期待される形式でマスキングされる (最初8文字 + 残り13文字分の*)
        assert masked_key == "test-api*************"
        assert len(masked_key) == len(config.api_key)

    def test_get_masked_api_key_short_key(self):
        """境界値ケース: 短いAPIキーのマスキング"""
        # Given: 10文字のAPIキー（バリデーション通過する最小長）
        config_data = {
            "api_key": "short12345",  # 10文字
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        config = GeminiConfig(**config_data)

        # When: マスキングされたAPIキーを取得
        masked_key = config.get_masked_api_key()

        # Then: 最初8文字 + 残り2文字分の*
        assert masked_key == "short123**"

    def test_get_masked_api_key_exactly_eight_chars(self):
        """境界値ケース: ちょうど8文字のAPIキー（バリデーション無視でテスト）"""
        # Given: 8文字のAPIキー（バリデーションをスキップして直接作成）
        config = GeminiConfig.__new__(GeminiConfig)
        config.api_key = "eight123"  # 8文字
        config.model = "gemini-2.5-pro"
        config.temperature = 0.7
        config.max_tokens = 1000
        config.safety_settings = None

        # When: マスキングされたAPIキーを取得
        masked_key = config.get_masked_api_key()

        # Then: 全文字がマスキングされる
        assert masked_key == "********"


class TestGeminiConfigValidation:
    """GeminiConfig バリデーション機能のテスト"""

    @pytest.mark.parametrize(
        "invalid_api_key", [None, 123, [], {}, "", "short"]  # 10文字未満
    )
    def test_invalid_api_key_types(self, invalid_api_key):
        """パラメータ化テスト: 無効なAPIキーの型"""
        # Given: 無効なAPIキー
        config_data = {
            "api_key": invalid_api_key,
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(ValueError):
            GeminiConfig(**config_data)

    @pytest.mark.parametrize(
        "invalid_temperature", [-1.0, 1.1, 2.0, "0.7", None, []]  # 文字列
    )
    def test_invalid_temperature_values(self, invalid_temperature):
        """パラメータ化テスト: 無効なtemperature値"""
        # Given: 無効なtemperature
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": invalid_temperature,
            "max_tokens": 1000,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(ValueError):
            GeminiConfig(**config_data)

    @pytest.mark.parametrize(
        "invalid_max_tokens",
        [0, -1, 10000, "1000", None, 3.14],  # 上限超過  # 文字列  # float
    )
    def test_invalid_max_tokens_values(self, invalid_max_tokens):
        """パラメータ化テスト: 無効なmax_tokens値"""
        # Given: 無効なmax_tokens
        config_data = {
            "api_key": "test-api-key-12345678",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": invalid_max_tokens,
        }

        # When & Then: ValueErrorが発生する
        with pytest.raises(ValueError):
            GeminiConfig(**config_data)
