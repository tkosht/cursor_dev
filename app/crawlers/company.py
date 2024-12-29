"""
企業情報クローラー

企業の基本情報、財務情報、ニュースを取得します。
"""

from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler
from app.models.company import Company
from app.models.financial import Financial
from app.models.news import News


class CompanyCrawler(BaseCrawler):
    """企業情報クローラー"""

    def __init__(self, company_code: str, *args, **kwargs):
        """初期化

        Args:
            company_code: 企業コード
            *args: 基底クラスに渡す位置引数
            **kwargs: 基底クラスに渡すキーワード引数
        """
        super().__init__(company_code, *args, **kwargs)
        # 企業コードに応じたベースURLを設定
        self.base_urls = {
            "9843": "https://www.nitorihd.co.jp",
            "7203": "https://global.toyota",
            "6758": "https://www.sony.com",
        }
        self.base_url = self.base_urls.get(company_code)
        if not self.base_url:
            raise ValueError(f"企業コード {company_code} のURLが未定義です")

    def _crawl(self) -> None:
        """クロール処理を実行"""
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
        """
        try:
            # 企業情報ページのスクレイピング
            url = urljoin(self.base_url, "/ir/library/annual/")
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # データの抽出（ニトリHDの場合）
            if self.company_code == "9843":
                info = {
                    "name": "ニトリホールディングス",
                    "stock_exchange": "東証プライム",
                    "industry": "小売業",
                    "description": soup.find("div", class_="about-company").text.strip()
                    if soup.find("div", class_="about-company")
                    else "家具・インテリア用品の企画・販売",
                }
            else:
                # 他の企業の場合はダミーデータを返す
                info = {
                    "name": "未取得",
                    "stock_exchange": "東証プライム",
                    "industry": "未取得",
                    "description": "未取得",
                }
            return info
        except Exception as e:
            self._log_warning(f"企業情報の取得に失敗: {str(e)}")
            raise

    def _crawl_financial_info(self) -> List[Dict]:
        """財務情報を取得

        Returns:
            財務情報のリスト
        """
        try:
            # 財務情報ページのスクレイピング
            url = urljoin(self.base_url, "/ir/library/result/")
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # データの抽出（ニトリHDの場合）
            financials = []
            if self.company_code == "9843":
                for table in soup.find_all("table", class_="financial-table"):
                    for row in table.find_all("tr")[1:]:  # ヘッダーをスキップ
                        cols = row.find_all("td")
                        if len(cols) >= 5:
                            financial = {
                                "fiscal_year": int(
                                    cols[0].text.strip().replace("年度", "")
                                ),
                                "period_type": "通期",
                                "revenue": float(cols[1].text.strip().replace(",", "")),
                                "operating_income": float(
                                    cols[2].text.strip().replace(",", "")
                                ),
                                "net_income": float(
                                    cols[3].text.strip().replace(",", "")
                                ),
                            }
                            financials.append(financial)
            else:
                # 他の企業の場合はダミーデータを返す
                financials.append(
                    {
                        "fiscal_year": 2023,
                        "period_type": "通期",
                        "revenue": 1000000000,
                        "operating_income": 100000000,
                        "net_income": 50000000,
                    }
                )
            return financials
        except Exception as e:
            self._log_warning(f"財務情報の取得に失敗: {str(e)}")
            raise

    def _crawl_news(self) -> List[Dict]:
        """ニュースを取得

        Returns:
            ニュース情報のリスト
        """
        try:
            # ニュースページのスクレイピング
            url = urljoin(self.base_url, "/ir/news/")
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # データの抽出（ニトリHDの場合）
            news_list = []
            if self.company_code == "9843":
                for article in soup.find_all("dl", class_="news-list"):
                    date = article.find("dt").text.strip()
                    title = article.find("dd").text.strip()
                    link = article.find("a")["href"] if article.find("a") else ""

                    news = {
                        "title": title,
                        "url": urljoin(self.base_url, link) if link else "",
                        "published_at": datetime.strptime(date, "%Y.%m.%d"),
                        "source": "IR情報",
                    }
                    news_list.append(news)
            else:
                # 他の企業の場合はダミーデータを返す
                news_list.append(
                    {
                        "title": "サンプルニュース",
                        "url": f"{self.base_url}/news/sample",
                        "published_at": datetime.now(),
                        "source": "IR情報",
                    }
                )
            return news_list
        except Exception as e:
            self._log_warning(f"ニュースの取得に失敗: {str(e)}")
            raise

    def _save_data(
        self, company_info: Dict, financials: List[Dict], news_list: List[Dict]
    ) -> None:
        """データを保存

        Args:
            company_info: 企業情報
            financials: 財務情報のリスト
            news_list: ニュース情報のリスト
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
