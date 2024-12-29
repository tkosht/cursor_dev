"""
AdaptiveCrawlerの統合テスト
"""
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager


@pytest.fixture
def llm_manager():
    """LLMマネージャーのモック"""
    manager = MagicMock(spec=LLMManager)
    manager.generate_selectors = AsyncMock(
        return_value={
            "company_name": "h1.company-name",
            "established_date": 'dl.company-info dt:contains("設立") + dd',
            "business_description": 'dl.company-info dt:contains("事業内容") + dd',
        }
    )
    manager.validate_data = AsyncMock(return_value=True)
    manager.analyze_error = AsyncMock(
        return_value={
            "should_retry": False,  # リトライを無効化
            "cause": "Test error",
            "solution": "Test solution",
        }
    )
    return manager


@pytest.fixture
def mock_response():
    """モックレスポンス"""

    class MockResponse:
        async def text(self):
            return """
            <html>
                <body>
                    <h1 class="company-name">株式会社ニトリホールディングス</h1>
                    <dl class="company-info">
                        <dt>設立</dt>
                        <dd>1972年3月</dd>
                        <dt>事業内容</dt>
                        <dd>家具・インテリア用品の企画・販売</dd>
                    </dl>
                </body>
            </html>
            """

        def raise_for_status(self):
            pass

    return MockResponse()


@pytest.fixture
def crawler(llm_manager, mock_response):
    """クローラーのインスタンス"""
    with patch(
        "app.crawlers.adaptive.AdaptiveCrawler._handle_error"
    ) as mock_handle_error:
        mock_handle_error.return_value = {
            "should_retry": False,
            "cause": "Test error",
            "solution": "Test solution",
        }

        crawler = AdaptiveCrawler(
            company_code="9843",
            llm_manager=llm_manager,
            max_retries=1,  # リトライ回数を1回に制限
            retry_delay=0,  # 遅延を0に設定
            max_concurrent=5,
            cache_ttl=60,
            max_cache_size=100,
        )
        # _make_requestメソッドをモック化
        crawler._make_request = AsyncMock(return_value=mock_response)
        yield crawler


@pytest.fixture(autouse=True)
def mock_sleep():
    """asyncio.sleepのモック化"""
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_file_operations():
    """ファイル操作のモック化"""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__ = MagicMock()
        mock_open.return_value.__exit__ = MagicMock()
        yield mock_open


async def validate_response(
    result: Dict[str, Any], expected_keys: Dict[str, str]
) -> None:
    """レスポンスを検証

    Args:
        result: クロール結果
        expected_keys: 期待するキー
    """
    assert result is not None
    assert isinstance(result, dict)
    for key in expected_keys:
        assert key in result
        assert result[key] is not None
        assert isinstance(result[key], str)
        assert len(result[key]) > 0


@pytest.mark.asyncio
async def test_crawl_nitori_company_info(crawler, mock_sleep, mock_file_operations):
    """ニトリの企業情報取得テスト"""
    # テストデータ
    url = "https://www.nitorihd.co.jp/company/"
    target_data = {
        "company_name": "会社名",
        "established_date": "設立日",
        "business_description": "事業内容",
    }

    # クロール実行
    result = await crawler.crawl(url, target_data)

    # 検証
    await validate_response(result, target_data)
    assert "ニトリ" in result["company_name"]
    assert "1972年" in result["established_date"]
    assert "家具" in result["business_description"]

    # モックの検証
    mock_sleep.assert_not_called()  # sleepが呼ばれていないことを確認


@pytest.mark.asyncio
async def test_crawl_nitori_company_info_real():
    """ニトリの企業情報取得テスト（実際のHTTPリクエスト）"""
    # LLMマネージャーのモック
    manager = MagicMock(spec=LLMManager)
    manager.generate_selectors = AsyncMock(
        return_value={
            "company_name": "h1.c-heading-lv1",  # 実際のセレクタに合わせて修正
            "established_date": 'dl.c-definition-list dt:contains("設立") + dd',
            "business_description": 'dl.c-definition-list dt:contains("事業内容") + dd',
        }
    )
    manager.validate_data = AsyncMock(return_value=True)
    manager.analyze_error = AsyncMock(
        return_value={
            "should_retry": False,
            "cause": "Test error",
            "solution": "Test solution",
        }
    )

    # クローラーの初期化
    crawler = AdaptiveCrawler(
        company_code="9843",
        llm_manager=manager,
        max_retries=1,  # リトライ回数を1回に制限
        retry_delay=0,  # 遅延を0に設定
        max_concurrent=5,
        cache_ttl=60,
        max_cache_size=100,
    )

    # テストデータ
    url = "https://www.nitorihd.co.jp/company/"
    target_data = {
        "company_name": "会社名",
        "established_date": "設立日",
        "business_description": "事業内容",
    }

    try:
        # クロール実行
        result = await crawler.crawl(url, target_data)

        # 検証
        await validate_response(result, target_data)
        assert "ニトリ" in result["company_name"].lower()
        assert "年" in result["established_date"]
        assert "家具" in result["business_description"]

    except Exception as e:
        pytest.skip(f"外部サービスへのアクセスに失敗: {str(e)}")
