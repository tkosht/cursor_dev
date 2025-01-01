"""Extraction manager for handling data extraction from web pages."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from ..exceptions import ExtractionError, NoValidDataError
from ..monitoring.monitor import Monitor

logger = logging.getLogger(__name__)


class ExtractionManager:
    """Manager class for extracting data from web pages."""

    def __init__(self, monitor: Optional[Monitor] = None):
        """Initialize the extraction manager.

        Args:
            monitor: Optional monitor for tracking extraction metrics.
        """
        self.monitor = monitor or Monitor()

    async def extract_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from a web page using the provided selectors.

        Args:
            url: The URL to extract data from.
            selectors: Dictionary of field names and their corresponding CSS selectors.

        Returns:
            Dictionary containing the extracted data.

        Raises:
            ExtractionError: If data extraction fails.
            NoValidDataError: If no valid data could be extracted.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise ExtractionError(f"Failed to fetch URL: {e}")

        soup = BeautifulSoup(html, "html.parser")
        data = {}

        for field, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if not elements:
                    logger.warning(f"No elements found for selector '{selector}' at {url}")
                    continue

                data[field] = [elem.get_text(strip=True) for elem in elements]
            except Exception as e:
                logger.error(f"Failed to extract {field} using selector '{selector}' at {url}: {e}")
                continue

        if not data:
            raise NoValidDataError(f"No valid data could be extracted from {url}")

        return data

    async def extract_multiple(
        self, urls: List[str], selectors: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Extract data from multiple URLs concurrently.

        Args:
            urls: List of URLs to extract data from.
            selectors: Dictionary of field names and their corresponding CSS selectors.

        Returns:
            List of dictionaries containing the extracted data.
        """
        tasks = [self.extract_data(url, selectors) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        extracted_data = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to extract data from {url}: {result}")
                continue
            extracted_data.append(result)

        return extracted_data 