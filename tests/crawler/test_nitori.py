"""Test module for Nitori crawler."""
from pathlib import Path

import pytest

from app.crawler.nitori import NitoriCrawler


@pytest.fixture
def crawler():
    """Create a test crawler instance."""
    storage_dir = Path("tests/data/nitori")
    return NitoriCrawler(storage_dir=storage_dir, headless=True)


def test_crawler_initialization(crawler):
    """Test crawler initialization."""
    assert crawler.base_url == "https://www.nitorihd.co.jp"
    assert crawler.ir_url == "https://www.nitorihd.co.jp/ir/"
    assert crawler.company_info_url == "https://www.nitorihd.co.jp/company/"


@pytest.mark.skip(reason="Requires browser interaction")
def test_crawler_context_manager(crawler):
    """Test crawler context manager."""
    with crawler as c:
        assert c.browser is not None
        assert c.page is not None

    assert crawler.browser is None
    assert crawler.page is None


@pytest.mark.skip(reason="Requires browser interaction")
@pytest.mark.integration
def test_get_company_info(crawler):
    """Test getting company information."""
    with crawler as c:
        company_info = c._get_company_info()
        assert isinstance(company_info, dict)
        assert "name" in company_info
        assert "company_profile" in company_info
        assert "updated_at" in company_info


@pytest.mark.skip(reason="Requires browser interaction")
@pytest.mark.integration
def test_get_financial_info(crawler):
    """Test getting financial information."""
    with crawler as c:
        financial_info = c._get_financial_info()
        assert isinstance(financial_info, dict)
        assert "financial_reports" in financial_info
        assert "updated_at" in financial_info
