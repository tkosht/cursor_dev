"""
AdaptiveCrawlerのテスト
"""
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager


class MockResponse:
    """モックレスポンス"""

    def __init__(self, html: str = "<html><body><div>Test Content</div></body></html>"):
        self._html = html

    async def text(self) -> str:
        """HTMLテキストを返す"""
        return self._html

    def raise_for_status(self):
        """ステータスチェック"""
        pass


@pytest.fixture
def llm_manager():
    """LLMマネージャーのモック"""
    manager = MagicMock(spec=LLMManager)
    manager.analyze_html_structure = AsyncMock(
        return_value={
            "validation_rules": {
                "title": {"type": "string", "required": True},
                "price": {"type": "number", "required": True},
            }
        }
    )
    manager.generate_selectors = AsyncMock(
        return_value={"title": "h1.product-title", "price": "span.product-price"}
    )
    manager.validate_data = AsyncMock(return_value=True)
    manager.analyze_error = AsyncMock(
        return_value={
            "should_retry": True,
            "cause": "Network error",
            "solution": "Retry with backoff",
        }
    )
    return manager


@pytest.fixture
def crawler(llm_manager):
    """クローラーのインスタンス"""
    return AdaptiveCrawler(
        company_code="9843",
        llm_manager=llm_manager,
        max_retries=3,
        retry_delay=0.1,
        timeout=aiohttp.ClientTimeout(total=1),  # テスト用に短いタイムアウトを設定
    )


@pytest.mark.asyncio
async def test_crawl_success(crawler):
    """正常系のテスト"""
    # テストデータ
    url = "https://example.com/product"
    target_data = {"title": "Product title", "price": "Product price"}

    # _make_requestをモック化
    crawler._make_request = AsyncMock(
        return_value=MockResponse(
            """
        <html>
            <body>
                <h1 class="product-title">Test Product</h1>
                <span class="product-price">1000円</span>
            </body>
        </html>
        """
        )
    )

    # クロール実行
    result = await crawler.crawl(url, target_data)

    # 検証
    assert result is not None
    assert isinstance(result, dict)
    assert "title" in result
    assert "price" in result
    assert result["title"] == "Test Product"
    assert result["price"] == "1000円"
    assert crawler.llm_manager.generate_selectors.called
    assert crawler.llm_manager.validate_data.called


@pytest.mark.asyncio
async def test_crawl_retry(crawler):
    """リトライのテスト"""
    # テストデータ
    url = "https://example.com/product"
    target_data = {"title": "Product title", "price": "Product price"}

    # 最初の2回は失敗、3回目で成功するように設定
    mock_response = MockResponse(
        """
        <html>
            <body>
                <h1 class="product-title">Test Product</h1>
                <span class="product-price">1000円</span>
            </body>
        </html>
        """
    )
    crawler._make_request = AsyncMock(
        side_effect=[aiohttp.ClientError(), aiohttp.ClientError(), mock_response]
    )

    # クロール実行
    result = await crawler.crawl(url, target_data)

    # 検証
    assert result is not None
    assert isinstance(result, dict)
    assert crawler._make_request.call_count == 3
    assert result["title"] == "Test Product"
    assert result["price"] == "1000円"


@pytest.mark.asyncio
async def test_crawl_max_retries_exceeded(crawler):
    """最大リトライ回数超過のテスト"""
    # テストデータ
    url = "https://example.com/product"
    target_data = {"title": "Product title", "price": "Product price"}

    # 常に失敗するように設定
    crawler._make_request = AsyncMock(side_effect=aiohttp.ClientError("Network error"))

    # クロール実行
    with pytest.raises(aiohttp.ClientError) as exc_info:
        await crawler.crawl(url, target_data)

    # 検証
    assert str(exc_info.value) == "Network error"
    assert crawler._make_request.call_count == crawler.max_retries + 1
    assert crawler.retry_count == crawler.max_retries


@pytest.mark.asyncio
async def test_crawl_validation_failed(crawler):
    """データ検証失敗のテスト"""
    # テストデータ
    url = "https://example.com/product"
    target_data = {"title": "Product title", "price": "Product price"}

    # _make_requestをモック化
    crawler._make_request = AsyncMock(return_value=MockResponse())

    # 検証に失敗するように設定
    crawler.llm_manager.validate_data = AsyncMock(return_value=False)

    # クロール実行
    with pytest.raises(ValueError) as exc_info:
        await crawler.crawl(url, target_data)

    # 検証
    assert str(exc_info.value) == "データの検証に失敗しました"
    assert crawler.llm_manager.validate_data.called
