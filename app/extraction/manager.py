"""
データ抽出マネージャー

Webページからの情報抽出を管理します。
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from app.errors.url_analysis_errors import ExtractionError


class ExtractionManager:
    """データ抽出を管理するクラス"""

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Args:
            timeout: リクエストタイムアウト（秒）
            max_retries: 最大リトライ回数
            headers: HTTPヘッダー
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    async def extract(
        self,
        url: str,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """データを抽出

        Args:
            url: 対象URL
            target_data: 抽出対象データの定義

        Returns:
            抽出したデータ

        Raises:
            ExtractionError: 抽出に失敗した場合
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise ExtractionError(
                            f"ステータスコード {response.status}",
                            url=url
                        )
                    content = await response.text()
                    return await self._extract_data(content, target_data)
            except asyncio.TimeoutError:
                raise ExtractionError("タイムアウト", url=url)
            except aiohttp.ClientError as e:
                raise ExtractionError(f"リクエストエラー: {str(e)}", url=url)

    async def extract_company_info(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """企業情報を抽出

        Args:
            url: 対象URL
            selectors: 抽出用のセレクター

        Returns:
            企業情報

        Raises:
            ExtractionError: 抽出に失敗した場合
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise ExtractionError(
                            f"ステータスコード {response.status}",
                            url=url
                        )
                    content = await response.text()
                    return self._extract_company_info(content, selectors)
            except asyncio.TimeoutError:
                raise ExtractionError("タイムアウト", url=url)
            except aiohttp.ClientError as e:
                raise ExtractionError(f"リクエストエラー: {str(e)}", url=url)

    async def extract_financial_info(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """財務情報を抽出

        Args:
            url: 対象URL
            selectors: 抽出用のセレクター

        Returns:
            財務情報のリスト

        Raises:
            ExtractionError: 抽出に失敗した場合
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise ExtractionError(
                            f"ステータスコード {response.status}",
                            url=url
                        )
                    content = await response.text()
                    return self._extract_financial_info(content, selectors)
            except asyncio.TimeoutError:
                raise ExtractionError("タイムアウト", url=url)
            except aiohttp.ClientError as e:
                raise ExtractionError(f"リクエストエラー: {str(e)}", url=url)

    def _extract_company_info(
        self,
        content: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """企業情報を抽出

        Args:
            content: HTMLコンテンツ
            selectors: 抽出用のセレクター

        Returns:
            企業情報
        """
        soup = BeautifulSoup(content, "html.parser")
        company_info = {}

        # 企業名の抽出
        if name_elem := soup.select_one(selectors.get("name")):
            company_info["name"] = name_elem.text.strip()

        # 事業内容の抽出
        description = "企業情報の詳細は取得できませんでした"
        for row in soup.find_all("tr"):
            if row.find("th") and "事業内容" in row.find("th").text:
                description = row.find("td").text.strip()
        company_info["description"] = description

        # 設立日の抽出
        for row in soup.find_all("tr"):
            if row.find("th") and "設立" in row.find("th").text:
                date_text = row.find("td").text.strip()
                try:
                    company_info["established_date"] = datetime.strptime(
                        date_text,
                        "%Y年%m月%d日"
                    ).date()
                except ValueError:
                    pass

        return company_info

    def _extract_financial_info(
        self,
        content: str,
        selectors: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """財務情報を抽出

        Args:
            content: HTMLコンテンツ
            selectors: 抽出用のセレクター

        Returns:
            財務情報のリスト
        """
        soup = BeautifulSoup(content, "html.parser")
        financials = []

        if table := soup.select_one(selectors.get("table")):
            for row in table.select(selectors.get("rows", "tr"))[1:]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    try:
                        year_text = cols[0].text.strip().replace("年度", "")
                        financial = {
                            "fiscal_year": str(year_text),
                            "period_type": "FULL_YEAR",
                            "period_end_date": datetime(
                                int(year_text), 3, 31
                            ).date(),
                            "revenue": self._parse_amount(cols[1].text.strip()),
                            "operating_income": self._parse_amount(
                                cols[2].text.strip()
                            ),
                            "net_income": self._parse_amount(cols[3].text.strip()),
                        }
                        financials.append(financial)
                    except (ValueError, IndexError):
                        continue

        return financials

    def _parse_amount(self, text: str) -> Optional[float]:
        """金額をパース

        Args:
            text: 金額テキスト

        Returns:
            パースした金額（パース失敗時はNone）
        """
        try:
            # カンマと単位を除去
            amount = text.replace(",", "").replace("円", "")
            # 単位の変換
            if "百万" in amount:
                amount = float(amount.replace("百万", "")) * 1_000_000
            elif "億" in amount:
                amount = float(amount.replace("億", "")) * 100_000_000
            else:
                amount = float(amount)
            return amount
        except ValueError:
            return None

    def calculate_validation_score(
        self,
        extracted_data: Dict[str, Any],
        expected_schema: Dict[str, Any]
    ) -> float:
        """検証スコアを計算

        Args:
            extracted_data: 抽出したデータ
            expected_schema: 期待するスキーマ

        Returns:
            検証スコア（0.0 - 1.0）
        """
        if not extracted_data or not expected_schema:
            return 0.0

        total_fields = len(expected_schema)
        valid_fields = 0

        for field, expected_type in expected_schema.items():
            if field in extracted_data:
                value = extracted_data[field]
                if isinstance(value, expected_type):
                    valid_fields += 1
                elif expected_type == float and value is not None:
                    valid_fields += 0.5  # 数値として扱える場合は部分的に正しいとみなす

        return valid_fields / total_fields 