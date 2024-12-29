"""
設定のテスト
"""
import os
import tempfile

import yaml

from app.config.settings import GlobalSettings, get_settings, load_settings


def test_default_settings():
    """デフォルト設定のテスト"""
    settings = GlobalSettings()

    assert settings.llm.default_model == "gemini-2.0-flash-exp"
    assert settings.llm.temperature == 0.1
    assert settings.llm.max_retries == 3

    assert settings.crawler.max_concurrent == 5
    assert settings.crawler.update_interval == 3600
    assert settings.crawler.timeout == 30
    assert settings.crawler.retry_interval == 60


def test_settings_from_dict():
    """辞書からの設定読み込みテスト"""
    config_dict = {
        "llm": {"default_model": "gpt-4o", "temperature": 0.2, "max_retries": 5},
        "crawler": {
            "max_concurrent": 10,
            "update_interval": 7200,
            "timeout": 60,
            "retry_interval": 120,
        },
    }

    settings = GlobalSettings.model_validate(config_dict)

    assert settings.llm.default_model == "gpt-4o"
    assert settings.llm.temperature == 0.2
    assert settings.llm.max_retries == 5

    assert settings.crawler.max_concurrent == 10
    assert settings.crawler.update_interval == 7200
    assert settings.crawler.timeout == 60
    assert settings.crawler.retry_interval == 120


def test_settings_file_io():
    """設定ファイルの入出力テスト"""
    # テスト用の設定
    settings = GlobalSettings(
        llm={"default_model": "gpt-4o", "temperature": 0.2, "max_retries": 5},
        crawler={
            "max_concurrent": 10,
            "update_interval": 7200,
            "timeout": 60,
            "retry_interval": 120,
        },
    )

    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False
    ) as temp_file:
        settings.save_to_file(temp_file.name)

        # 保存された内容を確認
        with open(temp_file.name, "r", encoding="utf-8") as f:
            saved_dict = yaml.safe_load(f)
            assert saved_dict["llm"]["default_model"] == "gpt-4o"
            assert saved_dict["crawler"]["max_concurrent"] == 10

        # 設定を読み込み
        loaded_settings = GlobalSettings.load_from_file(temp_file.name)
        assert loaded_settings.llm.default_model == "gpt-4o"
        assert loaded_settings.crawler.max_concurrent == 10

    # 一時ファイルを削除
    os.unlink(temp_file.name)


def test_get_settings():
    """グローバル設定の取得テスト"""
    settings = get_settings()
    assert isinstance(settings, GlobalSettings)
    assert settings.llm.default_model == "gemini-2.0-flash-exp"


def test_load_settings():
    """設定ファイルからの読み込みテスト"""
    # テスト用の設定ファイル
    config_dict = {
        "llm": {"default_model": "gpt-4o", "temperature": 0.2, "max_retries": 5},
        "crawler": {
            "max_concurrent": 10,
            "update_interval": 7200,
            "timeout": 60,
            "retry_interval": 120,
        },
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False
    ) as temp_file:
        yaml.safe_dump(config_dict, temp_file)
        temp_file.flush()

        # 設定を読み込み
        settings = load_settings(temp_file.name)
        assert settings.llm.default_model == "gpt-4o"
        assert settings.crawler.max_concurrent == 10

    # 一時ファイルを削除
    os.unlink(temp_file.name)
