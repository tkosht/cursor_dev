"""Nitori Holdings crawler module."""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ..parser.llm_parser import LLMParser
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class NitoriCrawler(BaseCrawler):
    """Crawler for Nitori Holdings website."""

    def __init__(
        self,
        storage_dir: Path = Path("data/nitori"),
        headless: bool = True
    ) -> None:
        """Initialize Nitori crawler.

        Args:
            storage_dir: Directory to store downloaded files
            headless: Whether to run browser in headless mode
        """
        super().__init__(
            base_url="https://www.nitorihd.co.jp",
            storage_dir=storage_dir,
            headless=headless
        )
        self.ir_url = f"{self.base_url}/ir/"
        self.company_info_url = f"{self.base_url}/company/about/"
        
        # LLMパーサーの初期化
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.parser = LLMParser(api_key=api_key)

    def _get_company_info(self) -> Dict[str, Any]:
        """Get basic company information.

        Returns:
            Dictionary containing company information
        """
        if not self.page:
            raise RuntimeError("Browser session not started")

        logger.info("Fetching company information...")
        self.page.goto(self.company_info_url)
        self.page.wait_for_load_state("networkidle")

        # ページ全体のHTMLを取得
        html_content = self.page.content()

        # 抽出したい項目の定義
        expected_fields = {
            "設立": "会社の設立日",
            "資本金": "会社の資本金額",
            "従業員数": "従業員の総数",
            "事業内容": "主な事業内容の説明",
            "本社所在地": "本社の住所"
        }

        # LLMを使用してパース
        parsed_data = self.parser.parse(
            html_content=html_content,
            page_type="company_info",
            expected_fields=expected_fields
        )

        if not parsed_data:
            logger.warning("Falling back to selector-based parsing")
            return self._get_company_info_fallback()

        return {
            "name": "株式会社ニトリホールディングス",
            "company_profile": parsed_data["extracted_data"],
            "business_summary": {},
            "updated_at": datetime.now().isoformat(),
            "confidence": parsed_data["confidence"]
        }

    def _get_company_info_fallback(self) -> Dict[str, Any]:
        """Fallback method for getting company information using selectors.

        Returns:
            Dictionary containing company information
        """
        company_info = {
            "name": "株式会社ニトリホールディングス",
            "company_profile": {},
            "business_summary": {},
            "updated_at": datetime.now().isoformat()
        }

        selectors = {
            "設立": ".c-about-info__list dt:has-text('設立') + dd",
            "資本金": ".c-about-info__list dt:has-text('資本金') + dd",
            "従業員数": ".c-about-info__list dt:has-text('従業員数') + dd",
            "事業内容": ".c-about-info__list dt:has-text('事業内容') + dd",
            "本社所在地": ".c-about-info__list dt:has-text('本社所在地') + dd"
        }

        for key, selector in selectors.items():
            value = self._get_text_content(selector)
            if value:
                company_info["company_profile"][key] = value

        return company_info

    def _get_text_content(self, selector: str) -> Optional[str]:
        """Get text content from element.

        Args:
            selector: CSS selector

        Returns:
            Text content if found, None otherwise
        """
        try:
            element = self.page.wait_for_selector(selector, timeout=5000)
            if element:
                return element.inner_text().strip()
        except PlaywrightTimeoutError:
            logger.warning(f"Element not found: {selector}")
        return None

    def _get_financial_info(self) -> Dict[str, Any]:
        """Get financial information.

        Returns:
            Dictionary containing financial information
        """
        if not self.page:
            raise RuntimeError("Browser session not started")

        logger.info("Fetching financial information...")
        self.page.goto(f"{self.ir_url}library/result.html")
        self.page.wait_for_load_state("networkidle")

        financial_info = {
            "financial_reports": [],
            "updated_at": datetime.now().isoformat()
        }

        # 決算短信PDFのダウンロード
        try:
            # 決算短信のリンクを探す
            pdf_links = self.page.query_selector_all("a:has-text('決算短信')")
            for link in pdf_links:
                href = link.get_attribute("href")
                if not href:
                    continue

                # PDFのURLを構築
                pdf_url = urljoin(self.base_url, href)
                filename = Path(href).name
                
                try:
                    self._download_pdf(pdf_url, filename)
                    financial_info["financial_reports"].append({
                        "url": pdf_url,
                        "filename": filename,
                        "downloaded_at": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Failed to download PDF {filename}: {str(e)}")

        except Exception as e:
            logger.error(f"Error while fetching financial information: {str(e)}")

        logger.info(f"Found {len(financial_info['financial_reports'])} financial reports")
        return financial_info

    def _download_pdf(self, url: str, filename: str) -> None:
        """Download PDF file.

        Args:
            url: URL of the PDF file
            filename: Name to save the file as

        Raises:
            requests.RequestException: If download fails
        """
        pdf_dir = self.storage_dir / "pdf"
        pdf_dir.mkdir(exist_ok=True)

        logger.info(f"Downloading PDF: {filename}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        file_path = pdf_dir / filename
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully downloaded PDF: {filename}")

    def crawl(self) -> Dict[str, Any]:
        """Crawl Nitori Holdings website.

        Returns:
            Dictionary containing all extracted data
        """
        try:
            data = {
                "company_info": self._get_company_info(),
                "financial_info": self._get_financial_info(),
                "crawled_at": datetime.now().isoformat()
            }
            return data
        except Exception as e:
            logger.error(f"Crawling failed: {str(e)}")
            raise
