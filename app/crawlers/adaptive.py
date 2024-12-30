"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.crawlers.base import BaseCrawler
from app.llm.manager import LLMManager

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ファイルハンドラーの設定
file_handler = logging.FileHandler("adaptive_crawler.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class AdaptiveCrawler(BaseCrawler):
    """LLMを使用した適応型クローラー"""

    def __init__(
        self,
        company_code: str,
        llm_manager: Optional[LLMManager] = None,
        session: Optional[Session] = None,
        **kwargs,
    ):
        """初期化

        Args:
            company_code: 企業コード
            llm_manager: LLMマネージャー
            session: データベースセッション
            **kwargs: その他のパラメータ
        """
        # AdaptiveCrawler固有のパラメータを抽出
        self.retry_delay = kwargs.pop("retry_delay", 1)
        self.max_concurrent = kwargs.pop("max_concurrent", 5)
        
        # タイムアウト関連のパラメータを抽出
        timeout_total = kwargs.pop("timeout_total", 60)
        timeout_connect = kwargs.pop("timeout_connect", 20)
        timeout_read = kwargs.pop("timeout_read", 20)
        
        # 基底クラスの初期化（残りのkwargsを渡す）
        super().__init__(company_code, session=session, **kwargs)

        # AdaptiveCrawler固有の初期化
        self.company_code = company_code
        self.llm_manager = llm_manager or LLMManager()
        self.retry_count = 0
        self.max_retries = kwargs.get("max_retries", 3)
        
        # タイムアウト設定
        self.timeout = aiohttp.ClientTimeout(
            total=timeout_total,
            connect=timeout_connect,
            sock_read=timeout_read
        )
        
        # ヘッダー設定
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "no-cache",
            "DNT": "1",
            "Sec-GPC": "1",
            "Pragma": "no-cache",
            "Referer": "https://www.google.com/"
        }
        
        # ロガーの設定
        self.logger = logger

        # 並行処理の制御
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # セッション管理
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリーポイント"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了処理"""
        if self._session:
            await self._session.close()
            self._session = None

    async def _fetch_page(self, url: str) -> str:
        """ページを取得する

        Args:
            url: 取得対象のURL

        Returns:
            取得したHTMLコンテンツ
        """
        self._log_debug("ページ取得開始")
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout
            )
        async with self._session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
        self._log_debug(f"ページ取得完了: {len(html)}バイト")
        return html

    async def _process_page(
        self,
        html: str,
        target_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """ページを処理する

        Args:
            html: HTMLコンテンツ
            target_data: 取得対象データの辞書

        Returns:
            抽出したデータの辞書
        """
        # ページ構造を解析
        self._log_debug("ページ構造解析開始")
        soup = BeautifulSoup(html, "html.parser")
        self._log_debug("ページ構造解析完了")

        # セレクタを生成
        self._log_debug("セレクタ生成開始")
        selectors = await self.llm_manager.generate_selectors(soup, target_data)
        self._log_debug(f"セレクタ生成完了: {selectors}")

        # データを抽出
        self._log_debug("データ抽出開始")
        extracted_data = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                extracted_data[key] = elements[0].get_text(strip=True)
        self._log_debug(f"データ抽出完了: {extracted_data}")

        # データを検証
        self._log_debug("データ検証開始")
        is_valid = await self.llm_manager.validate_data(extracted_data, target_data)
        if not is_valid:
            raise ValueError("データの検証に失敗しました")
        self._log_debug("データ検証完了")

        return extracted_data

    async def _handle_error(
        self,
        error: Exception,
        retry_count: int,
        error_type: str
    ) -> None:
        """エラーを処理する

        Args:
            error: 発生したエラー
            retry_count: 現在のリトライ回数
            error_type: エラーの種類を示す文字列
        """
        self._log_warning(
            f"{error_type}（リトライ {retry_count}/{self.max_retries}）: {str(error)}"
        )
        if retry_count > self.max_retries:
            self._log_error(f"{error_type}（最大リトライ回数超過）: {str(error)}")
            raise error

    async def crawl(self, url: str, target_data: Dict[str, str]) -> Dict[str, Any]:
        """クロール処理を実行

        Args:
            url: クロール対象のURL
            target_data: 取得対象データの辞書

        Returns:
            抽出したデータの辞書

        Raises:
            ValueError: データの検証に失敗した場合
            aiohttp.ClientError: HTTP通信に失敗した場合
            Exception: その他のエラーが発生した場合
        """
        async with self.semaphore:
            retry_count = 0
            last_error = None
            
            while retry_count <= self.max_retries:
                try:
                    # ページ取得と処理
                    data = await self._fetch_and_process(url, target_data)
                    return data

                except aiohttp.ClientError as e:
                    retry_count += 1
                    last_error = e
                    await self._handle_error(e, retry_count, "HTTP通信エラー")

                except ValueError as e:
                    retry_count += 1
                    last_error = e
                    await self._handle_error(e, retry_count, "データ検証エラー")

                except Exception as e:
                    retry_count += 1
                    last_error = e
                    await self._handle_error(e, retry_count, "予期せぬエラー")

                # 指数バックオフでリトライ
                await asyncio.sleep(self.retry_delay * (2 ** (retry_count - 1)))

            if last_error:
                raise last_error

    async def _fetch_and_process(
        self,
        url: str,
        target_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """ページを取得して処理する

        Args:
            url: 取得対象のURL
            target_data: 取得対象データの辞書

        Returns:
            抽出したデータの辞書
        """
        # ページ取得
        self._log_info(f"ページ取得開始: {url}")
        html = await self._fetch_page(url)
        self._log_info(f"ページ取得完了: {len(html)}バイト")

        # データ抽出
        self._log_info("データ抽出開始")
        data = await self._process_page(html, target_data)
        self._log_info(f"データ抽出完了: {data}")

        # データ検証
        if not await self.llm_manager.validate_data(data, target_data):
            raise ValueError("データの検証に失敗しました")

        return data

    def _log_debug(self, message: str) -> None:
        """デバッグログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.debug(message)

    def _log_info(self, message: str) -> None:
        """情報ログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.info(message)

    def _log_warning(self, message: str) -> None:
        """警告ログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.warning(message)

    def _log_error(self, message: str) -> None:
        """エラーログを出力

        Args:
            message: ログメッセージ
        """
        self.logger.error(message)

    async def close(self) -> None:
        """リソースのクリーンアップ"""
        if self._session:
            await self._session.close()
            self._session = None
        await super().close()

    async def analyze_site_structure(self, url: str) -> Dict[str, Any]:
        """サイト構造を解析する

        Args:
            url: 解析対象のURL

        Returns:
            Dict[str, Any]: 解析結果
            {
                "navigation": ナビゲーション要素の内容,
                "main_content": メインコンテンツの内容,
                "links": リンク一覧,
                "headings": 見出し一覧
            }
        """
        self._log_debug(f"サイト構造解析開始: {url}")
        
        try:
            # ページを取得
            html = await self._fetch_page(url)
            soup = BeautifulSoup(html, "html.parser")
            
            # ナビゲーション要素を抽出
            nav_elements = soup.find_all(["nav", "header", "menu"])
            navigation = " ".join([nav.get_text(strip=True) for nav in nav_elements])
            
            # メインコンテンツを抽出
            main_elements = soup.find_all(["main", "article", "div", "section"])
            main_content = " ".join([main.get_text(strip=True) for main in main_elements])
            
            # リンクを抽出
            links = [
                {
                    "text": a.get_text(strip=True),
                    "href": a.get("href", "")
                }
                for a in soup.find_all("a", href=True)
            ]
            
            # 見出しを抽出
            headings = [
                h.get_text(strip=True)
                for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            ]
            
            structure = {
                "navigation": navigation,
                "main_content": main_content,
                "links": links,
                "headings": headings
            }
            
            self._log_debug(f"サイト構造解析完了: {len(structure)} 要素")
            return structure
            
        except Exception as e:
            self._log_error(f"サイト構造解析エラー: {str(e)}")
            raise
    
    async def extract_data(self, url: str, target_data: Dict[str, str]) -> Dict[str, str]:
        """データを抽出する

        Args:
            url: 抽出対象のURL
            target_data: 抽出対象データの辞書
                {"revenue": "売上高", "profit": "営業利益"}のような形式

        Returns:
            Dict[str, str]: 抽出したデータの辞書
                {"revenue": "1,234,567円", "profit": "123,456円"}のような形式
        """
        self._log_debug(f"データ抽出開始: {url}")
        
        try:
            # サイト構造を解析
            structure = await self.analyze_site_structure(url)
            
            # LLMを使用してデータを抽出
            prompt = (
                "以下のサイト構造から、指定されたデータを抽出してください。\n"
                "抽出対象データ:\n"
            )
            for key, value in target_data.items():
                prompt += f"- {key}: {value}\n"
            prompt += f"\nサイト構造:\n{structure}\n"
            
            extracted_data = await self.llm_manager.llm.extract_data(prompt)
            
            # データを検証
            if not all(key in extracted_data for key in target_data.keys()):
                raise ValueError("必要なデータが抽出できませんでした")
            
            self._log_debug(f"データ抽出完了: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            self._log_error(f"データ抽出エラー: {str(e)}")
            raise
