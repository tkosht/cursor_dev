"""
企業クローラー

このモジュールは、企業情報をクロールするクローラーを提供します。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.financial import Financial, PeriodType
from app.models.news import News

from .base import BaseCrawler


class CompanyCrawler(BaseCrawler):
    """
    企業情報クローラー

    特定の企業の情報をクロールするクローラーです。

    Attributes:
        company_code (str): 企業コード
        base_url (str): 基本URL
    """

    def __init__(
        self,
        company_code: str,
        session: Optional[Session] = None,
        base_url: str = "https://www.nitorihd.co.jp"
    ):
        """
        企業クローラーを初期化します。

        Args:
            company_code (str): 企業コード
            session (Optional[Session]): データベースセッション
            base_url (str): 基本URL
        """
        super().__init__(session=session)
        self.company_code = company_code
        self.base_url = base_url.rstrip('/')

    def crawl(self) -> None:
        """
        企業情報のクロールを実行します。
        """
        # 企業情報の取得
        company_response = self._make_request(f"{self.base_url}/company/")
        if company_response:
            company_data = self.parse_company(company_response)
            self.save_company(company_data)

        # 財務情報の取得
        financial_response = self._make_request(f"{self.base_url}/ir/library/result.html")
        if financial_response:
            financial_data = self.parse_financial(financial_response)
            self.save_financial(financial_data)

        # ニュースの取得
        news_response = self._make_request(f"{self.base_url}/ir/news/")
        if news_response:
            news_data = self.parse_news(news_response)
            self.save_news(news_data)

    def parse_company(self, response: Any) -> Dict[str, Any]:
        """
        企業情報をパースします。

        Args:
            response (Any): HTTPレスポンス

        Returns:
            Dict[str, Any]: パースした企業情報
        """
        # 注: 実際の実装では、BeautifulSoupを使用してHTMLをパースします
        return {
            'company_code': self.company_code,
            'name': "ニトリホールディングス",
            'name_en': "Nitori Holdings Co., Ltd.",
            'description': "家具・インテリア用品の企画・販売",
            'established_date': datetime(1972, 3, 3).date(),
            'website_url': self.base_url,
            'stock_exchange': "東証プライム",
            'industry': "小売業"
        }

    def parse_financial(self, response: Any) -> List[Dict[str, Any]]:
        """
        財務情報をパースします。

        Args:
            response (Any): HTTPレスポンス

        Returns:
            List[Dict[str, Any]]: パースした財務情報のリスト
        """
        # 注: 実際の実装では、BeautifulSoupを使用してHTMLをパースします
        return [{
            'fiscal_year': "2023年度",
            'period_type': PeriodType.FULL_YEAR,
            'period_end_date': datetime(2024, 2, 20).date(),
            'revenue': 1000000000,
            'operating_income': 100000000
        }]

    def parse_news(self, response: Any) -> List[Dict[str, Any]]:
        """
        ニュースをパースします。

        Args:
            response (Any): HTTPレスポンス

        Returns:
            List[Dict[str, Any]]: パースしたニュースのリスト
        """
        # 注: 実際の実装では、BeautifulSoupを使用してHTMLをパースします
        return [{
            'title': "2024年2月期 第3四半期決算短信〔IFRS〕（連結）",
            'content': "当第3四半期連結累計期間の営業収益は6,481億71百万円...",
            'url': f"{self.base_url}/ir/news/2024/20240104.pdf",
            'published_at': datetime(2024, 1, 4, 15, 0),
            'source': "適時開示",
            'category': "決算情報"
        }]

    def save_company(self, data: Dict[str, Any]) -> None:
        """
        企業情報を保存します。

        Args:
            data (Dict[str, Any]): 保存する企業情報
        """
        company = Company(**data)
        self.session.add(company)
        self.save(company)

    def save_financial(self, data_list: List[Dict[str, Any]]) -> None:
        """
        財務情報を保存します。

        Args:
            data_list (List[Dict[str, Any]]): 保存する財務情報のリスト
        """
        company = self.session.query(Company).filter_by(
            company_code=self.company_code
        ).first()
        if not company:
            self.logger.error(f"Company not found: {self.company_code}")
            return

        for data in data_list:
            data['company_id'] = company.id
            financial = Financial(**data)
            self.session.add(financial)
        self.save(financial)

    def save_news(self, data_list: List[Dict[str, Any]]) -> None:
        """
        ニュースを保存します。

        Args:
            data_list (List[Dict[str, Any]]): 保存するニュースのリスト
        """
        company = self.session.query(Company).filter_by(
            company_code=self.company_code
        ).first()
        if not company:
            self.logger.error(f"Company not found: {self.company_code}")
            return

        for data in data_list:
            data['company_id'] = company.id
            news = News(**data)
            self.session.add(news)
        self.save(news) 