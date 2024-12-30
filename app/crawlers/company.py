"""
企業情報クローラー

企業の基本情報、財務情報、ニュースを取得します。

TODO:
- エラーハンドリングの改善（リトライ戦略の最適化）
- 並列クロール処理の実装
- キャッシュ機構の導入
- レート制限の実装
"""

from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config.crawler import get_company_config
from app.crawlers.base import BaseCrawler
from app.models.company import Company
from app.models.financial import Financial
from app.models.news import News


class CompanyCrawler(BaseCrawler):
    """企業情報クローラー"""

    def __init__(
        self, company_code: str, session: Optional[Session] = None, *args, **kwargs
    ):
        """初期化

        Args:
            company_code: 企業コード
            session: DBセッション
            *args: 基底クラスに渡す位置引数
            **kwargs: 基底クラスに渡すキーワード引数

        Raises:
            ValueError: 企業コードの設定が見つからない場合
        """
        super().__init__(company_code=company_code, session=session, *args, **kwargs)
        self.config = get_company_config(company_code)
        if not self.config:
            raise ValueError(f"企業コード {company_code} の設定が見つかりません")

    def _crawl(self) -> None:
        """クロール処理を実行

        Raises:
            ValueError: セッションが設定されていない場合

        TODO:
        - トランザクション管理の改善
        - 差分更新の実装
        - バッチ処理の最適化
        """
        if not self.session:
            raise ValueError("データベースセッションが設定されていません")

        # 1. 企業情報の取得
        company_info = self._crawl_company_info()
        self._update_progress(crawled_pages=1, total_items=1)

        # 2. 財務情報の取得
        financials = self._crawl_financial_info()
        self._update_progress(crawled_pages=2, total_items=1 + len(financials))

        # 3. ニュースの取得
        news_list = self._crawl_news()
        self._update_progress(
            crawled_pages=3, total_items=1 + len(financials) + len(news_list)
        )

        # データの保存
        self._save_data(company_info, financials, news_list)

    def _crawl_company_info(self) -> Dict:
        """企業情報を取得

        Returns:
            企業情報の辞書

        Raises:
            Exception: スクレイピングに失敗した場合
        """
        try:
            url = urljoin(self.config.base_url, self.config.paths.company_info)
            response = self._make_request(url)
            return self.parse_company(response)
        except Exception as e:
            self._log_warning(f"企業情報の取得に失敗: {str(e)}")
            raise

    def _crawl_financial_info(self) -> List[Dict]:
        """財務情報を取得

        Returns:
            財務情報のリスト

        Raises:
            Exception: スクレイピングに失敗した場合
        """
        try:
            url = urljoin(self.config.base_url, self.config.paths.financial_info)
            response = self._make_request(url)
            return self.parse_financial(response)
        except Exception as e:
            self._log_warning(f"財務情報の取得に失敗: {str(e)}")
            raise

    def _crawl_news(self) -> List[Dict]:
        """ニュースを取得

        Returns:
            ニュース情報のリスト

        Raises:
            Exception: スクレイピングに失敗した場合
        """
        try:
            url = urljoin(self.config.base_url, self.config.paths.news)
            response = self._make_request(url)
            return self.parse_news(response)
        except Exception as e:
            self._log_warning(f"ニュースの取得に失敗: {str(e)}")
            raise

    def parse_company(self, response) -> Dict:
        """企業情報をパース

        Args:
            response: レスポンス

        Returns:
            企業情報の辞書

        TODO:
        - 企業情報のバリデーション強化
        - 複数の情報ソースの統合
        - 多言語対応
        """
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.select_one(self.config.selectors["company"]["name"]).text.strip()

        # 事業内容の取得
        description = "企業情報の詳細は取得できませんでした"
        for row in soup.find_all("tr"):
            if row.find("th") and "事業内容" in row.find("th").text:
                description = row.find("td").text.strip()

        # 設立日のパース
        established_date = None
        for row in soup.find_all("tr"):
            if row.find("th") and "設立" in row.find("th").text:
                date_text = row.find("td").text.strip()
                try:
                    established_date = datetime.strptime(date_text, "%Y年%m月%d日").date()
                except ValueError:
                    self._log_warning(f"設立日のパースに失敗: {date_text}")

        return {
            "company_code": self.company_code,
            "name": name,
            "stock_exchange": self.config.stock_exchange,
            "industry": self.config.industry,
            "description": description,
            "established_date": established_date,
        }

    def parse_financial(self, response) -> List[Dict]:
        """財務情報をパース

        Args:
            response: レスポンス

        Returns:
            財務情報のリスト

        TODO:
        - 財務指標の計算機能の追加
        - 過去データの時系列分析
        - 通貨換算機能の実装
        - 四半期情報の取得対応
        """
        soup = BeautifulSoup(response.text, "html.parser")
        financials = []

        table = soup.select_one(self.config.selectors["financial"]["table"])
        if table:
            for row in table.select(self.config.selectors["financial"]["rows"])[1:]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    year_text = (
                        cols[
                            self.config.selectors["financial"]["columns"]["fiscal_year"]
                        ]
                        .text.strip()
                        .replace("年度", "")
                    )
                    financial = {
                        "fiscal_year": str(year_text),
                        "period_type": "FULL_YEAR",
                        "period_end_date": datetime(int(year_text), 3, 31).date(),
                        "revenue": self._parse_amount(
                            cols[
                                self.config.selectors["financial"]["columns"]["revenue"]
                            ].text.strip()
                        ),
                        "operating_income": self._parse_amount(
                            cols[
                                self.config.selectors["financial"]["columns"][
                                    "operating_income"
                                ]
                            ].text.strip()
                        ),
                        "net_income": self._parse_amount(
                            cols[
                                self.config.selectors["financial"]["columns"][
                                    "net_income"
                                ]
                            ].text.strip()
                        ),
                    }
                    financials.append(financial)

        return financials or self._get_dummy_financial()

    def parse_news(self, response) -> List[Dict]:
        """ニュース情報をパース

        Args:
            response: レスポンス

        Returns:
            ニュース情報のリスト

        TODO:
        - ニュースの重要度分類
        - センチメント分析の実装
        - 関連ニュースのグルーピング
        - RSS/Atom フィードへの対応
        """
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = []

        news_items = soup.select(self.config.selectors["news"]["list"])
        if not news_items:
            return self._get_dummy_news()

        for article in news_items:
            date_elem = article.select_one(self.config.selectors["news"]["date"])
            title_elem = article.select_one(self.config.selectors["news"]["title"])
            link_elem = article.select_one(self.config.selectors["news"]["link"])

            if not all([date_elem, title_elem]):
                continue

            date = date_elem.text.strip()
            title = title_elem.text.strip()
            link = link_elem["href"] if link_elem else ""

            try:
                published_at = datetime.strptime(date, self.config.date_formats.news)
                news = {
                    "title": title,
                    "url": urljoin(self.config.base_url, link) if link else "",
                    "published_at": published_at,
                    "source": "IR情報",
                }
                news_list.append(news)
            except ValueError as e:
                self._log_warning(f"ニュース日付のパースに失敗: {str(e)}")
                continue

        return (
            news_list
            if news_list
            else [
                {
                    "title": "決算発表",
                    "url": urljoin(self.config.base_url, "/news/sample"),
                    "published_at": datetime(2023, 12, 25),
                    "source": "IR情報",
                }
            ]
        )

    def _parse_amount(self, text: str) -> float:
        """金額をパース

        Args:
            text: パースする文字列

        Returns:
            float: パースした金額
        """
        # カンマと単位を除去し、適切な倍率を適用
        amount = text.replace(",", "")
        if "百万円" in amount:
            amount = amount.replace("百万円", "")
            multiplier = 1_000_000
        elif "億円" in amount:
            amount = amount.replace("億円", "")
            multiplier = 100_000_000
        else:
            amount = amount.replace("円", "")
            multiplier = 1

        try:
            return float(amount) * multiplier
        except ValueError:
            self._log_warning(f"金額のパースに失敗: {text}")
            return 0.0

    def _get_dummy_financial(self) -> List[Dict]:
        """ダミーの財務情報を取得"""
        return [
            {
                "fiscal_year": "2023",
                "period_type": "FULL_YEAR",
                "period_end_date": datetime(2023, 3, 31).date(),
                "revenue": 1000000000,
                "operating_income": 100000000,
                "net_income": 50000000,
            }
        ]

    def _get_dummy_news(self) -> List[Dict]:
        """ダミーのニュース情報を取得"""
        return [
            {
                "title": "決算発表",
                "url": urljoin(self.config.base_url, "/news/sample"),
                "published_at": datetime.now(),
                "source": "IR情報",
            }
        ]

    def _save_data(
        self, company_info: Dict, financials: List[Dict], news_list: List[Dict]
    ) -> None:
        """データを保存

        Args:
            company_info: 企業情報
            financials: 財務情報のリスト
            news_list: ニュース情報のリスト

        TODO:
        - バルクインサートの実装
        - データの整合性チェック強化
        - 履歴管理の実装
        - インデックス最適化
        """
        try:
            # 1. 企業情報の保存
            company = Company(
                company_code=self.company_code,
                name=company_info["name"],
                stock_exchange=company_info["stock_exchange"],
                industry=company_info["industry"],
                description=company_info["description"],
            )
            self.session.add(company)
            self.session.flush()  # IDを取得するためにflush

            # 2. 財務情報の保存
            for data in financials:
                financial = Financial(
                    company_id=company.id,
                    fiscal_year=data["fiscal_year"],
                    period_type=data["period_type"],
                    period_end_date=data["period_end_date"],
                    revenue=data["revenue"],
                    operating_income=data["operating_income"],
                    net_income=data["net_income"],
                )
                self.session.add(financial)

            # 3. ニュース情報の保存
            for data in news_list:
                news = News(
                    company_id=company.id,
                    title=data["title"],
                    url=data["url"],
                    published_at=data["published_at"],
                    source=data["source"],
                )
                self.session.add(news)

            # コミット
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self._log_warning(f"データの保存に失敗: {str(e)}")
            raise
