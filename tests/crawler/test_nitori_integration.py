"""Integration tests for Nitori crawler."""
from pathlib import Path

import pytest

from app.crawler.nitori import NitoriCrawler


@pytest.mark.integration
def test_get_company_info_integration():
    """Integration test for getting company information."""
    storage_dir = Path("test_data")
    crawler = NitoriCrawler(storage_dir=storage_dir)
    
    with crawler:
        company_info = crawler._get_company_info()
    
    assert company_info["name"] == "株式会社ニトリホールディングス"
    assert "company_profile" in company_info
    assert "confidence" in company_info


@pytest.mark.integration
def test_get_financial_info_integration():
    """Integration test for getting financial information."""
    storage_dir = Path("test_data")
    crawler = NitoriCrawler(storage_dir=storage_dir)
    
    with crawler:
        financial_info = crawler._get_financial_info()
    
    assert "financial_reports" in financial_info
    assert "updated_at" in financial_info


@pytest.mark.integration
def test_crawl_integration():
    """Integration test for crawling."""
    storage_dir = Path("test_data")
    crawler = NitoriCrawler(storage_dir=storage_dir)
    
    data = crawler.crawl()
    
    assert "company_info" in data
    assert "financial_info" in data
    assert "crawled_at" in data 