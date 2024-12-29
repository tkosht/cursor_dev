"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import aiohttp
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
        self.retry_delay = kwargs.pop('retry_delay', 1)
        super().__init__(company_code, session=session, **kwargs)
        
        self.llm_manager = llm_manager or LLMManager()
        self.retry_count = 0
        self.max_retries = kwargs.get('max_retries', 3)
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        self.default_model = kwargs.get('default_model', 'gemini-2.0-flash-exp')
    
    async def crawl(self, url: str, target_data: Dict[str, str]) -> Dict[str, Any]:
        """クロール処理を実行
        
        Args:
            url: クロール対象のURL
            target_data: 取得対象データの辞書
        
        Returns:
            抽出したデータの辞書
        """
        retry_count = 0
        max_retries = 3
        last_error = None
        
        while retry_count <= max_retries:
            try:
                self._log_debug(f'クロール開始: {url} (試行回数: {retry_count + 1})')
                start_time = time.time()

                # 1. ページを取得
                self._log_debug('ページ取得開始')
                response = await self._make_request(url)
                html = await response.text()
                self._log_debug(f'ページ取得完了: {len(html)}バイト')

                # 2. ページ構造を解析
                self._log_debug('ページ構造解析開始')
                soup = BeautifulSoup(html, 'html.parser')
                self._log_debug('ページ構造解析完了')

                # 3. セレクタを生成
                self._log_debug('セレクタ生成開始')
                selectors = await self.llm_manager.generate_selectors(soup, target_data)
                self._log_debug(f'セレクタ生成完了: {selectors}')

                # 4. データを抽出
                self._log_debug('データ抽出開始')
                extracted_data = await self._extract_data(soup, selectors)
                self._log_debug(f'データ抽出完了: {extracted_data}')

                # 5. データを検証
                self._log_debug('データ検証開始')
                is_valid = await self.llm_manager.validate_data(extracted_data, target_data)
                if not is_valid:
                    raise ValueError('抽出データの検証に失敗しました')
                self._log_debug('データ検証完了')

                # 6. 処理時間を計測
                end_time = time.time()
                processing_time = end_time - start_time
                self._log_info(f'処理時間: {processing_time:.2f}秒')

                return extracted_data

            except Exception as e:
                last_error = e
                retry_count += 1
                error_context = {
                    'url': url,
                    'target_data': target_data,
                    'retry_count': retry_count - 1,
                    'error': str(e)
                }
                analysis = await self._handle_error(str(e), error_context)
                
                if retry_count <= max_retries and analysis['should_retry']:
                    backoff = 0.2 * (2 ** (retry_count - 1))  # 指数バックオフ
                    self._log_info(f'{backoff}秒後にリトライします (エラー: {str(e)})')
                    await asyncio.sleep(backoff)
                    continue
                else:
                    break

        if last_error:
            self._log_error(f'最大リトライ回数({max_retries})を超えました。最後のエラー: {str(last_error)}')
            raise last_error
    
    async def _retry_with_backoff(self) -> None:
        """バックオフ付きリトライ"""
        delay = self.retry_delay * (2 ** self.retry_count)
        self._log_info(f'{delay}秒後にリトライします')
        await asyncio.sleep(delay)
    
    async def _make_request(self, url: str) -> aiohttp.ClientResponse:
        """HTTPリクエストを実行
        
        Args:
            url: リクエスト先のURL
        
        Returns:
            レスポンス
        
        Raises:
            aiohttp.ClientError: リクエストに失敗した場合
            asyncio.TimeoutError: タイムアウトした場合
        """
        async with aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return response
    
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
    
    async def _extract_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """データを抽出
        
        Args:
            soup: BeautifulSoupオブジェクト
            selectors: セレクタの辞書
        
        Returns:
            抽出したデータの辞書
        """
        data = {}
        
        for key, selector in selectors.items():
            try:
                self._log_debug(f'セレクタ {selector} でデータ抽出開始')
                element = soup.select_one(selector)
                if element:
                    data[key] = element.text.strip()
                    self._log_debug(f'データ抽出成功: {key} = {data[key]}')
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
    ) -> Dict[str, Any]:
        """エラーを処理
        
        Args:
            error: 発生したエラー
            context: エラーコンテキスト
        
        Returns:
            エラー分析結果の辞書
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
        
        return {
            'should_retry': isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError)),
            'cause': str(error),
            'solution': analysis.get('solution', 'リトライを実行')
        }

    def _log_error(self, message: str) -> None:
        """エラーメッセージをログに記録

        Args:
            message: ログメッセージ
        """
        logging.error(message)

    def _log_info(self, message: str) -> None:
        """情報メッセージをログに記録

        Args:
            message: ログメッセージ
        """
        logging.info(message)

    def _log_warning(self, message: str) -> None:
        """警告メッセージをログに記録

        Args:
            message: ログメッセージ
        """
        logging.warning(message)

    def _log_debug(self, message: str) -> None:
        """デバッグメッセージをログに記録

        Args:
            message: ログメッセージ
        """
        logging.debug(message) 