"""Nitori Holdings crawler module."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urljoin

import requests

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
        self.company_info_url = f"{self.base_url}/company/"

    def _get_company_info(self) -> Dict[str, Any]:
        """Get basic company information.

        Returns:
            Dictionary containing company information
        """
        if not self.page:
            raise RuntimeError("Browser session not started")

        self.page.goto(self.company_info_url)
        self.page.wait_for_load_state("networkidle")

        company_info = {
            "name": "株式会社ニトリホールディングス",
            "company_profile": {},
            "business_summary": {},
            "updated_at": datetime.now().isoformat()
        }

        # 会社概要の取得
        profile_content = self.page.query_selector(".company-profile")
        if profile_content:
            rows = profile_content.query_selector_all("tr")
            for row in rows:
                cells = row.query_selector_all("th, td")
                if len(cells) == 2:
                    key = cells[0].inner_text().strip()
                    value = cells[1].inner_text().strip()
                    company_info["company_profile"][key] = value

        return company_info

    def _get_financial_info(self) -> Dict[str, Any]:
        """Get financial information.

        Returns:
            Dictionary containing financial information
        """
        if not self.page:
            raise RuntimeError("Browser session not started")

        self.page.goto(f"{self.ir_url}/library/")
        self.page.wait_for_load_state("networkidle")

        financial_info = {
            "financial_reports": [],
            "updated_at": datetime.now().isoformat()
        }

        # 決算短信PDFのダウンロード
        pdf_links = self.page.query_selector_all("a[href*='.pdf']")
        for link in pdf_links:
            href = link.get_attribute("href")
            if href and "tanshin" in href.lower():
                pdf_url = urljoin(self.base_url, href)
                filename = Path(href).name
                self._download_pdf(pdf_url, filename)
                financial_info["financial_reports"].append({
                    "url": pdf_url,
                    "filename": filename,
                    "downloaded_at": datetime.now().isoformat()
                })

        return financial_info

    def _download_pdf(self, url: str, filename: str) -> None:
        """Download PDF file.

        Args:
            url: URL of the PDF file
            filename: Name to save the file as
        """
        pdf_dir = self.storage_dir / "pdf"
        pdf_dir.mkdir(exist_ok=True)

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = pdf_dir / filename
            with open(file_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded PDF: {filename}")
        else:
            logger.error(f"Failed to download PDF: {url}")

    def crawl(self) -> Dict[str, Any]:
        """Crawl Nitori Holdings website.

        Returns:
            Dictionary containing all extracted data
        """
        data = {
            "company_info": self._get_company_info(),
            "financial_info": self._get_financial_info(),
            "crawled_at": datetime.now().isoformat()
        }
        return data
