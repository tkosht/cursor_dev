"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.crawlers.base import BaseCrawler
from app.llm.manager import LLMManager


class AdaptiveCrawler(BaseCrawler):
    """LLMを使用した適応型クローラー"""

    def __init__(
        self,
        company_code: str,
        llm_manager: Optional[LLMManager] = None,
        session: Optional[Session] = None,
        **kwargs
    ):
        """初期化
        
        Args:
            company_code: 企業コード
            llm_manager: LLMマネージャー
            session: データベースセッション
            **kwargs: 基底クラスに渡すキーワード引数
        """
        super().__init__(company_code, session=session, **kwargs)
        self.llm_manager = llm_manager or LLMManager()
        self.retry_count = 0
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 1)
    
    async def crawl(self, url: str, target_data: Dict[str, str]) -> Dict[str, Any]:
        """クロール処理を実行
        
        Args:
            url: クロール対象のURL
            target_data: 取得対象データの辞書
        
        Returns:
            抽出したデータの辞��
        """
        try:
            # 1. ページを取得
            response = await self._make_request(url)
            html = response.text
            
            # 2. ページ構造を分析
            analysis = await self._analyze_page_structure(html)
            self._log_info(f'ページ構造分析結果: {analysis}')
            
            # 3. セレクタを生成
            selectors = await self._generate_selectors(html, target_data)
            self._log_info(f'生成されたセレクタ: {selectors}')
            
            # 4. データを抽出
            data = self._extract_data(html, selectors)
            self._log_info(f'抽出されたデータ: {data}')
            
            # 5. データを検証
            rules = analysis.get('validation_rules', {})
            is_valid = await self._validate_data(data, rules)
            
            if not is_valid:
                raise ValueError('データの検証に失敗しました')
            
            return data
        
        except Exception as e:
            context = {
                'url': url,
                'target_data': target_data,
                'retry_count': self.retry_count
            }
            await self._handle_error(e, context)
            
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                await self._retry_with_backoff()
                return await self.crawl(url, target_data)
            
            raise
    
    async def _retry_with_backoff(self) -> None:
        """バックオフ付きリトライ"""
        delay = self.retry_delay * (2 ** self.retry_count)
        self._log_info(f'{delay}秒後にリトライします')
        await asyncio.sleep(delay)
    
    async def _make_request(self, url: str) -> Any:
        """HTTPリクエストを実行
        
        Args:
            url: リクエスト先のURL
        
        Returns:
            レスポンス
        """
        # TODO: 実装
        # 現在は仮実装
        class DummyResponse:
            def __init__(self):
                self.text = '<html><body><h1>Sample</h1></body></html>'
        
        await asyncio.sleep(0.1)  # 実際のリクエストを模擬
        return DummyResponse()
    
    async def _analyze_page_structure(self, html: str) -> Dict[str, Any]:
        """ページ構造を分析
        
        Args:
            html: HTML文字列
        
        Returns:
            分析結果の辞書
        """
        # LLMを使用してページ構造を分析
        analysis = await self.llm_manager.analyze_html_structure(html)
        return analysis
    
    async def _generate_selectors(
        self,
        html: str,
        target_data: Dict[str, str]
    ) -> Dict[str, str]:
        """セレクタを生成
        
        Args:
            html: HTML文字列
            target_data: 取得対象データの辞書
        
        Returns:
            セレクタの辞書
        """
        # LLMを使用してセレクタを生成
        selectors = await self.llm_manager.generate_selectors(html, target_data)
        return selectors
    
    def _extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """データを抽出
        
        Args:
            html: HTML文字列
            selectors: セレクタの辞書
        
        Returns:
            抽出したデータの辞書
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        for key, selector in selectors.items():
            try:
                element = soup.select_one(selector)
                if element:
                    data[key] = element.text.strip()
                else:
                    self._log_warning(f'セレクタ {selector} でデータが見つかりません')
                    data[key] = None
            except Exception as e:
                self._log_warning(f'データ抽出エラー: {str(e)}')
                data[key] = None
        
        return data
    
    async def _validate_data(
        self,
        data: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> bool:
        """データを検証
        
        Args:
            data: 検証対象データの辞書
            rules: 検証ルールの辞書
        
        Returns:
            検証結果（True/False）
        """
        # LLMを使用してデータを検証
        is_valid = await self.llm_manager.validate_data(data, rules)
        return is_valid
    
    async def _handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """エラーを処理
        
        Args:
            error: 発生したエラー
            context: エラーコンテキスト
        """
        # LLMを使用してエラーを分析
        analysis = await self.llm_manager.analyze_error(
            self.default_model,
            str(error)
        )
        
        # エラー情報をログに記録
        self._log_error(
            f'エラー発生: {str(error)}\n'
            f'コンテキスト: {context}\n'
            f'分析結果: {analysis}'
        ) 