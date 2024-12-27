from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ..models.company import Company
from ..models.financial import Financial
from ..models.news import News
from .base import BaseCrawler


class CompanyCrawler(BaseCrawler):
    """
    企業情報クローラー
    
    Attributes:
        company_code (str): 企業コード
        base_url (str): 基本URL
    """
    
    def __init__(self, company_code: str, *args, **kwargs):
        """
        初期化
        
        Args:
            company_code: 企業コード
            *args: BaseCrawlerに渡す位置引数
            **kwargs: BaseCrawlerに渡すキーワード引数
        """
        super().__init__(*args, **kwargs)
        self.company_code = company_code
        self.base_url = "https://www.nitorihd.co.jp"
    
    def crawl(self) -> None:
        """企業情報のクロール"""
        try:
            # 1. 企業情報の取得
            company_response = self._make_request(f"{self.base_url}/company/")
            company_data = self.parse_company(company_response)
            company = Company(**company_data)
            self.save(company)
            
            # 2. 財務情報の取得
            financial_response = self._make_request(f"{self.base_url}/ir/library/result.html")
            financial_data_list = self.parse_financial(financial_response)
            for data in financial_data_list:
                data['company_id'] = company.id
                financial = Financial(**data)
                self.save(financial)
            
            # 3. ニュースの取得
            news_response = self._make_request(f"{self.base_url}/ir/news/")
            news_data_list = self.parse_news(news_response)
            for data in news_data_list:
                data['company_id'] = company.id
                news = News(**data)
                self.save(news)
                
        except Exception as e:
            self.logger.error(f"Crawl failed: {str(e)}")
            raise
    
    def parse_company(self, response: requests.Response) -> Dict[str, Any]:
        """
        企業情報のパース
        
        Args:
            response: レスポンスオブジェクト
            
        Returns:
            Dict: パースした企業情報
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        company_info = soup.select_one('.company-info')
        
        # 設立日を取得
        established_date_row = company_info.find('th', string='設立')
        if not established_date_row:
            raise ValueError("設立日が見つかりません")
        established_date = established_date_row.find_next_sibling('td').text.strip()
        
        # 事業内容を取得
        description_row = company_info.find('th', string='事業内容')
        if not description_row:
            raise ValueError("事業内容が見つかりません")
        description = description_row.find_next_sibling('td').text.strip()
        
        # 企業名を取得
        company_name = company_info.select_one('.company-name')
        if not company_name:
            raise ValueError("企業名が見つかりません")
        
        return {
            'company_code': self.company_code,
            'name': company_name.text.strip(),
            'established_date': datetime.strptime(established_date, '%Y年%m月%d日').date(),
            'description': description,
            'website_url': self.base_url,
            'stock_exchange': '東証プライム',
            'industry': '小売業'
        }
    
    def parse_financial(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        財務情報のパース
        
        Args:
            response: レスポンスオブジェクト
            
        Returns:
            List[Dict]: パースした財務情報のリスト
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for row in soup.select('.financial-table tr')[1:]:  # ヘッダー行をス���ップ
            cols = row.select('td')
            if not cols:
                continue
                
            # 金額のクリーニング（カンマと単位を削除）
            revenue = int(cols[1].text.strip().replace(',', '').replace('百万円', '')) * 1_000_000
            operating_income = int(cols[2].text.strip().replace(',', '').replace('百万円', '')) * 1_000_000
            
            results.append({
                'fiscal_year': cols[0].text.strip(),
                'period_type': '通期',
                'revenue': revenue,
                'operating_income': operating_income,
                'period_end_date': datetime.strptime(
                    f"{cols[0].text.strip()}年3月31日",
                    '%Y年%m月%d日'
                ).date()
            })
        
        return results
    
    def parse_news(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        ニュース情報のパース
        
        Args:
            response: レスポンスオブジェクト
            
        Returns:
            List[Dict]: パースしたニュース情報のリスト
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for item in soup.select('.news-list li'):
            date = item.select_one('.date').text.strip()
            title = item.select_one('.title').text.strip()
            link = item.select_one('a')['href']
            
            results.append({
                'title': title,
                'url': urljoin(self.base_url, link),
                'published_at': datetime.strptime(date, '%Y.%m.%d'),
                'source': 'IR情報',
                'category': 'プレスリリース'
            })
        
        return results 