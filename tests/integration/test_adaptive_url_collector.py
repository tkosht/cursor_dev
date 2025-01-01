"""Integration tests for AdaptiveURLCollector."""

from unittest.mock import Mock

import pytest

from app.crawlers import AdaptiveURLCollector
from app.exceptions import URLCollectionError
from app.llm.manager import LLMManager


@pytest.fixture
def llm_manager():
    """Create a mock LLM manager."""
    manager = Mock(spec=LLMManager)
    manager.analyze_structure.return_value = {
        "patterns": [
            {
                "selector": "nav a",
                "type": "link",
                "priority": "high"
            },
            {
                "selector": ".ir-links a",
                "type": "link",
                "priority": "high"
            }
        ]
    }
    return manager


@pytest.fixture
def collector(llm_manager):
    """Create an AdaptiveURLCollector instance."""
    return AdaptiveURLCollector(
        llm_manager=llm_manager,
        max_concurrent_requests=3,
        request_timeout=30.0,
        max_retries=3,
        allowed_domains=["test.local"]
    )


@pytest.mark.asyncio
async def test_collect_urls_adaptively_success(collector):
    """Test successful adaptive URL collection."""
    url = "https://test.local/company"
    urls = await collector.collect_urls_adaptively(url)
    
    assert isinstance(urls, list)
    assert all(isinstance(url, str) for url in urls)
    assert collector.llm_manager.analyze_structure.called


@pytest.mark.asyncio
async def test_collect_urls_with_context(collector):
    """Test URL collection with additional context."""
    url = "https://test.local/ir"
    context = {
        "company_type": "listed",
        "target_info": ["financial_reports", "press_releases"]
    }
    
    urls = await collector.collect_urls_adaptively(url, context)
    
    assert isinstance(urls, list)
    assert collector.llm_manager.analyze_structure.called
    call_args = collector.llm_manager.analyze_structure.call_args[0][0]
    assert "company_type" in call_args
    assert "target_info" in call_args


@pytest.mark.asyncio
async def test_domain_filtering(collector):
    """Test domain filtering functionality."""
    url = "https://test.local/company"
    collector.llm_manager.analyze_structure.return_value = {
        "patterns": [
            {
                "selector": "a",
                "type": "link",
                "priority": "high"
            }
        ]
    }
    
    urls = await collector.collect_urls_adaptively(url)
    
    assert all(
        u.startswith("https://test.local") or not u.startswith(("http://", "https://"))
        for u in urls
    )


@pytest.mark.asyncio
async def test_error_handling(collector):
    """Test error handling during URL collection."""
    url = "https://test.local/error"
    collector.llm_manager.analyze_structure.side_effect = Exception("LLM error")
    
    with pytest.raises(URLCollectionError):
        await collector.collect_urls_adaptively(url)


@pytest.mark.asyncio
async def test_pattern_learning(collector):
    """Test pattern learning functionality."""
    url = "https://test.local/company"
    initial_patterns = len(collector.extraction_patterns)
    
    await collector.collect_urls_adaptively(url)
    
    assert len(collector.extraction_patterns) > initial_patterns


@pytest.mark.asyncio
async def test_real_company_sites(collector):
    """Test URL collection from actual company sites."""
    test_urls = [
        "https://test.local/company/ir",
        "https://test.local/company/about",
        "https://test.local/company/news"
    ]
    
    for url in test_urls:
        urls = await collector.collect_urls_adaptively(url)
        assert isinstance(urls, list)
        assert len(urls) > 0 