"""
クローラーのモニタリング機能

クローラーのパフォーマンスとエラー情報を記録します。
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class CrawlerMetrics(BaseModel):
    """クローラーのメトリクス情報"""
    start_time: datetime
    end_time: Optional[datetime] = None
    company_code: str
    status: str
    error_count: int = 0
    warning_count: int = 0
    crawled_pages: int = 0
    total_items: int = 0


class CrawlerMonitor:
    """クローラーのモニタリングクラス"""
    
    def __init__(self, log_file: str = 'crawler.log'):
        """
        Args:
            log_file: ログファイルのパス
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # ファイルハンドラーの設定
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # アクティブなクローラーの状態管理
        self.active_crawlers: Dict[str, CrawlerMetrics] = {}
    
    def start_crawler(self, company_code: str) -> None:
        """クローラーの開始を記録
        
        Args:
            company_code: 企業コード
        """
        metrics = CrawlerMetrics(
            start_time=datetime.now(),
            company_code=company_code,
            status='running'
        )
        self.active_crawlers[company_code] = metrics
        self.logger.info(f'Started crawler for company {company_code}')
    
    def stop_crawler(self, company_code: str, status: str = 'completed') -> None:
        """クローラーの終了を記録
        
        Args:
            company_code: 企業コード
            status: 終了ステータス ('completed' or 'error')
        """
        if company_code in self.active_crawlers:
            metrics = self.active_crawlers[company_code]
            metrics.end_time = datetime.now()
            metrics.status = status
            self.logger.info(
                f'Stopped crawler for company {company_code} with status {status}'
            )
            # メトリクスの記録
            self._log_metrics(metrics)
            # アクティブリストから削除
            del self.active_crawlers[company_code]
    
    def log_error(self, company_code: str, error: Exception) -> None:
        """エラーを記録
        
        Args:
            company_code: 企業コード
            error: 発生したエラー
        """
        if company_code in self.active_crawlers:
            self.active_crawlers[company_code].error_count += 1
        self.logger.error(
            f'Error in crawler for company {company_code}: {str(error)}',
            exc_info=True
        )
    
    def log_warning(self, company_code: str, message: str) -> None:
        """警告を記録
        
        Args:
            company_code: 企業コード
            message: 警告メッセージ
        """
        if company_code in self.active_crawlers:
            self.active_crawlers[company_code].warning_count += 1
        self.logger.warning(
            f'Warning in crawler for company {company_code}: {message}'
        )
    
    def update_progress(
        self,
        company_code: str,
        crawled_pages: int,
        total_items: int
    ) -> None:
        """進捗状況を更新
        
        Args:
            company_code: 企業コード
            crawled_pages: クロール済みページ数
            total_items: 取得済みアイテム数
        """
        if company_code in self.active_crawlers:
            metrics = self.active_crawlers[company_code]
            metrics.crawled_pages = crawled_pages
            metrics.total_items = total_items
            self.logger.info(
                f'Progress for company {company_code}: '
                f'{crawled_pages} pages, {total_items} items'
            )
    
    def get_active_crawlers(self) -> List[str]:
        """実行中のクローラー一覧を取得
        
        Returns:
            実行中の企業コードリスト
        """
        return list(self.active_crawlers.keys())
    
    def get_metrics(self, company_code: str) -> Optional[CrawlerMetrics]:
        """クローラーのメトリクスを取得
        
        Args:
            company_code: 企業コード
        
        Returns:
            メトリクス情報。存在しない場合はNone
        """
        return self.active_crawlers.get(company_code)
    
    def _log_metrics(self, metrics: CrawlerMetrics) -> None:
        """メトリクス情報をログに記録
        
        Args:
            metrics: メトリクス情報
        """
        duration = (metrics.end_time - metrics.start_time).total_seconds()
        self.logger.info(
            f'Crawler metrics for company {metrics.company_code}:\n'
            f'Duration: {duration:.2f} seconds\n'
            f'Status: {metrics.status}\n'
            f'Error count: {metrics.error_count}\n'
            f'Warning count: {metrics.warning_count}\n'
            f'Crawled pages: {metrics.crawled_pages}\n'
            f'Total items: {metrics.total_items}'
        ) 