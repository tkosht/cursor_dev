"""
クローラー設定のテスト
"""

import os
from tempfile import NamedTemporaryFile

import pytest
from pydantic import ValidationError

from app.config.crawler import (CompanyConfigModel, ConfigLoader,
                                get_company_config)


def test_company_config_model_valid():
    """正常な設定値でのバリデーションテスト"""
    config = CompanyConfigModel(
        company_code="9843",
        base_url="https://www.nitorihd.co.jp",
        company_info_path="/company/",
        financial_info_path="/ir/library/result.html",
        news_info_path="/ir/news/"
    )
    assert config.company_code == "9843"
    assert config.base_url == "https://www.nitorihd.co.jp"
    assert config.company_info_path == "/company/"
    assert config.financial_info_path == "/ir/library/result.html"
    assert config.news_info_path == "/ir/news/"


def test_company_config_model_invalid_base_url():
    """不正なbase_urlでのバリデーションテスト"""
    with pytest.raises(ValidationError) as exc_info:
        CompanyConfigModel(
            company_code="9843",
            base_url="invalid-url",
        )
    assert "base_urlはhttp://またはhttps://で始まる必要があります" in str(exc_info.value)


def test_company_config_model_invalid_company_code():
    """不正なcompany_codeでのバリデーションテスト"""
    with pytest.raises(ValidationError) as exc_info:
        CompanyConfigModel(
            company_code="invalid",
            base_url="https://www.nitorihd.co.jp",
        )
    assert "company_codeは数字である必要があります" in str(exc_info.value)


def test_config_loader_file_not_found():
    """存在しない設定ファイルのテスト"""
    os.environ['COMPANY_CONFIG_PATH'] = 'non_existent.yaml'
    with pytest.raises(FileNotFoundError) as exc_info:
        ConfigLoader()
    assert "設定ファイルが見つかりません" in str(exc_info.value)
    del os.environ['COMPANY_CONFIG_PATH']


def test_config_loader_invalid_format():
    """不正な形式の設定ファイルのテスト"""
    with NamedTemporaryFile(mode='w', suffix='.yaml') as temp_file:
        temp_file.write("invalid: yaml")
        temp_file.flush()
        os.environ['COMPANY_CONFIG_PATH'] = temp_file.name
        with pytest.raises(ValueError) as exc_info:
            ConfigLoader()
        assert "無効な設定ファイル形式です" in str(exc_info.value)
    del os.environ['COMPANY_CONFIG_PATH']


def test_config_loader_valid_config():
    """正常な設定ファイルのテスト"""
    with NamedTemporaryFile(mode='w', suffix='.yaml') as temp_file:
        temp_file.write("""
companies:
  "9843":
    company_code: "9843"
    base_url: "https://www.nitorihd.co.jp"
    company_info_path: "/company/"
    financial_info_path: "/ir/library/result.html"
    news_info_path: "/ir/news/"
""")
        temp_file.flush()
        os.environ['COMPANY_CONFIG_PATH'] = temp_file.name
        loader = ConfigLoader()
        config = loader.get_config("9843")
        assert config is not None
        assert config.company_code == "9843"
        assert config.base_url == "https://www.nitorihd.co.jp"
    del os.environ['COMPANY_CONFIG_PATH']


def test_get_company_config_existing():
    """存在する企業コードでの設定取得テスト"""
    config = get_company_config("9843")
    assert config is not None
    assert config.company_code == "9843"
    assert config.base_url == "https://www.nitorihd.co.jp"


def test_get_company_config_non_existing():
    """存在しない企業コードでの設定取得テスト"""
    config = get_company_config("9999")
    assert config is None 