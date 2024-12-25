"""Test configuration and fixtures."""
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment."""
    os.environ["OPENAI_API_KEY"] = "test_key"
    yield
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch("app.parser.llm_parser.OpenAI") as mock:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="""
{
    "extracted_data": {
        "設立": "1972年3月",
        "資本金": "13,370百万円",
        "従業員数": "45,000名",
        "事業内容": "家具・インテリア用品の販売",
        "本社所在地": "札幌市北区"
    },
    "confidence": 0.95
}
"""
                    )
                )
            ]
        )
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_playwright():
    """Mock Playwright browser."""
    with patch("playwright.sync_api.sync_playwright") as mock:
        # ブラウザのモック
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # ページのメソッドをモック
        mock_page.goto = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.content.return_value = """
        <html>
            <body>
                <div class="company-info">
                    <dl>
                        <dt>設立</dt>
                        <dd>1972年3月</dd>
                        <dt>資本金</dt>
                        <dd>13,370百万円</dd>
                        <dt>従業員数</dt>
                        <dd>45,000名</dd>
                        <dt>事業内容</dt>
                        <dd>家具・インテリア用品の販売</dd>
                        <dt>本社所在地</dt>
                        <dd>札幌市北区</dd>
                    </dl>
                </div>
            </body>
        </html>
        """

        # ブラウザチェーンの設定
        mock_browser.chromium.launch.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # sync_playwright()の戻り値をモック
        mock_playwright = MagicMock()
        mock_playwright.chromium = mock_browser
        mock_playwright.start = MagicMock(return_value=mock_playwright)
        mock.return_value = mock_playwright

        yield mock 