"""
クローラー設定のテスト
"""

from tempfile import NamedTemporaryFile

import pytest

from app.config.crawler import CompanyConfig, CrawlerConfig, get_company_config


def test_company_config_valid():
    """正常な設定値でのバリデーションテスト"""
    config = CompanyConfig(
        base_url="https://www.nitorihd.co.jp",
        name="ニトリホールディングス",
        stock_exchange="東証プライム",
        industry="小売業",
        paths={
            "company_info": "/company/",
            "financial_info": "/ir/library/result.html",
            "news": "/ir/news/",
        },
        selectors={},
        date_formats={"news": "%Y.%m.%d"},
    )
    assert config.base_url == "https://www.nitorihd.co.jp"
    assert config.name == "ニトリホールディングス"
    assert config.paths.company_info == "/company/"
    assert config.paths.financial_info == "/ir/library/result.html"
    assert config.paths.news == "/ir/news/"


def test_crawler_config_file_not_found():
    """存在しない設定ファイルのテスト"""
    with pytest.raises(FileNotFoundError):
        CrawlerConfig("non_existent.yaml")


def test_crawler_config_invalid_format():
    """不正な形式の設定ファイルのテスト"""
    with NamedTemporaryFile(mode="w", suffix=".yaml") as temp_file:
        temp_file.write("invalid: yaml")
        temp_file.flush()
        with pytest.raises(KeyError):
            CrawlerConfig(temp_file.name)


def test_crawler_config_valid_config():
    """正常な設定ファイルのテスト"""
    with NamedTemporaryFile(mode="w", suffix=".yaml") as temp_file:
        temp_file.write(
            """
companies:
  "9843":
    base_url: "https://www.nitorihd.co.jp"
    name: "ニトリホールディングス"
    stock_exchange: "東証プライム"
    industry: "小売業"
    paths:
      company_info: "/company/"
      financial_info: "/ir/library/result.html"
      news: "/ir/news/"
    selectors: {}
    date_formats:
      news: "%Y.%m.%d"
"""
        )
        temp_file.flush()
        config = CrawlerConfig(temp_file.name)
        company = config.get_company_config("9843")
        assert company is not None
        assert company.base_url == "https://www.nitorihd.co.jp"
        assert company.name == "ニトリホールディングス"


def test_get_company_config_non_existing():
    """存在しない企業コードでの設定取得テスト"""
    config = get_company_config("9999")
    assert config is None
