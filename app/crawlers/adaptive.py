"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
import logging
import os
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


class RequestTracker:
    """リクエストの重複を制御するトラッカー"""

    def __init__(self):
        """初期化"""
        self._active_requests: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def track_request(
        self, key: str, operation: Any
    ) -> Any:
        """リクエストを追跡し、重複を防止する

        Args:
            key: リクエストの一意キー
            operation: 実行する非同期操作

        Returns:
            Any: 操作の結果
        """
        async with self._lock:
            if key in self._active_requests:
                self._log_debug(f"重複リクエストを検出: {key}")
                return await self._active_requests[key]

            task = asyncio.create_task(operation)
            self._active_requests[key] = task
            self._log_debug(f"新規リクエストを追跡開始: {key}")

        try:
            result = await task
            return result
        finally:
            async with self._lock:
                self._active_requests.pop(key, None)
                self._log_debug(f"リクエストの追跡を終了: {key}")

    def _log_debug(self, message: str) -> None:
        """デバッグログを出力"""
        logger.debug(message)


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
        timeout = kwargs.pop("timeout", None)
        connector = kwargs.pop("connector", None)
        
        # 基底クラスの初期化（必要なパラメータのみ渡す）
        super().__init__(company_code, session=session)

        # AdaptiveCrawler固有の初期化
        self.company_code = company_code
        self.llm_manager = llm_manager
        self._llm_initialized = False
        if not self.llm_manager:
            api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY_GEMINI not found in environment variables")
            self.llm_manager = LLMManager()

        self.retry_count = 0
        self.max_retries = kwargs.get("max_retries", 3)
        
        # タイムアウト設定
        self.timeout = timeout or aiohttp.ClientTimeout(
            total=60,
            connect=20,
            sock_read=20
        )
        
        # コネクタ設定
        self.connector = connector or aiohttp.TCPConnector(
            limit=10,
            enable_cleanup_closed=True,
            force_close=False,
            keepalive_timeout=60
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
        
        # リクエストトラッカーの初期化
        self.request_tracker = RequestTracker()
        
        # セッション管理
        self._session: Optional[aiohttp.ClientSession] = None

    def _generate_request_key(self, url: str, target_data: Any) -> str:
        """リクエストの一意キーを生成

        Args:
            url: クロール対象のURL
            target_data: 取得対象データ（辞書またはモデルオブジェクト）

        Returns:
            str: リクエストの一意キー
        """
        # target_dataを辞書に変換
        if hasattr(target_data, "__dict__"):
            # モデルオブジェクトの場合は__dict__を使用
            data_dict = {
                k: str(v) for k, v in target_data.__dict__.items()
                if not k.startswith("_")
            }
        elif isinstance(target_data, dict):
            # 辞書の場合はそのまま使用
            data_dict = target_data
        else:
            raise ValueError(f"Unsupported target_data type: {type(target_data)}")

        # 辞書をソートしてハッシュ化し、URLと組み合わせて一意なキーを生成
        sorted_items = sorted(data_dict.items())
        params_hash = hash(frozenset(sorted_items))
        return f"{url}:{params_hash}"

    async def crawl(self, url: str, target_data: Any) -> Dict[str, Any]:
        """クロール処理を実行

        Args:
            url: クロール対象のURL
            target_data: 取得対象データ（辞書またはモデルオブジェクト）

        Returns:
            Dict[str, Any]: 抽出したデータの辞書

        Raises:
            ValueError: データの検証に失敗した場合
            aiohttp.ClientError: HTTP通信に失敗した場合
            Exception: その他のエラーが発生した場合
        """
        request_key = self._generate_request_key(url, target_data)
        
        # リクエストトラッカーを使用して重複を制御
        return await self.request_tracker.track_request(
            request_key,
            self._execute_crawl(url, target_data)
        )

    async def _execute_crawl(
        self,
        url: str,
        target_data: Any
    ) -> Dict[str, Any]:
        """実際のクロール処理を実行

        Args:
            url: クロール対象のURL
            target_data: 取得対象データ（辞書またはモデルオブジェクト）

        Returns:
            Dict[str, Any]: 抽出したデータの辞書
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

    async def __aenter__(self):
        """非同期コンテキストマネージャのエントリーポイント"""
        # LLMの初期化
        if not self._llm_initialized and not self.llm_manager.llm:
            api_key = os.getenv("GOOGLE_API_KEY_GEMINI")
            await self.llm_manager.load_model("gemini-2.0-flash-exp", api_key)
            self._llm_initialized = True

        # セッションの初期化
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                connector=self.connector
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
                timeout=self.timeout,
                connector=self.connector
            )
        async with self._session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
        self._log_debug(f"ページ取得完了: {len(html)}バイト")
        return html

    async def _process_page(
        self,
        html: str,
        target_data: Any
    ) -> Dict[str, Any]:
        """ページを処理する

        Args:
            html: HTMLコンテンツ
            target_data: 取得対象データ（辞書またはモデルオブジェクト）

        Returns:
            抽出したデータの辞書
        """
        # target_dataを辞書に変換
        if hasattr(target_data, "__dict__"):
            # モデルオブジェクトの場合は__dict__を使用
            data_dict = {
                k: str(v) for k, v in target_data.__dict__.items()
                if not k.startswith("_")
            }
        elif isinstance(target_data, dict):
            # 辞書の場合はそのまま使用
            data_dict = target_data
        else:
            raise ValueError(f"Unsupported target_data type: {type(target_data)}")

        # ページ構造を解析
        self._log_debug("ページ構造解析開始")
        soup = BeautifulSoup(html, "html.parser")
        self._log_debug("ページ構造解析完了")

        # デバッグ用：テキストノードの内容を出力
        self._log_debug("テキストノード一覧:")
        for text in soup.stripped_strings:
            if len(text) > 1:  # 空白や1文字のテキストは除外
                self._log_debug(f"- {text}")

        # セレクタを生成
        self._log_debug("セレクタ生成開始")
        selectors = await self.llm_manager.generate_selectors(html, data_dict)
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
        is_valid = await self.llm_manager.validate_data(extracted_data, data_dict)
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

    async def _fetch_and_process(
        self,
        url: str,
        target_data: Any
    ) -> Dict[str, Any]:
        """ページを取得して処理する

        Args:
            url: 取得対象のURL
            target_data: 取得対象データ（辞書またはモデルオブジェクト）

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

        # target_dataを辞書に変換（検証用）
        if hasattr(target_data, "__dict__"):
            data_dict = {
                k: str(v) for k, v in target_data.__dict__.items()
                if not k.startswith("_")
            }
        elif isinstance(target_data, dict):
            data_dict = target_data
        else:
            raise ValueError(f"Unsupported target_data type: {type(target_data)}")

        # データ検証
        if not await self.llm_manager.validate_data(data, data_dict):
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

    async def get_ir_urls(self) -> Dict[str, str]:
        """企業のIRサイトのURLを取得する

        Returns:
            Dict[str, str]: IR情報の種類とURLのマッピング
            {
                "financial_results": "決算短信のURL",
                "press_releases": "プレスリリースのURL",
                "securities_reports": "有価証券報告書のURL"
            }
        """
        # 環境変数からAPIキーとCSE IDを取得
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("CSE_ID")
        if not api_key or not cse_id:
            raise ValueError("GOOGLE_API_KEY or CSE_ID not found in environment variables")

        # 企業コードから証券コードを生成（5桁の場合は先頭に0を付加）
        securities_code = self.company_code.zfill(4)
        
        urls = {}
        
        try:
            # 検索クエリを構築
            queries = {
                "financial_results": f"{securities_code} OR トヨタ自動車 決算短信 IR情報",
                "press_releases": f"{securities_code} OR トヨタ自動車 プレスリリース ニュースリリース",
                "securities_reports": f"{securities_code} OR トヨタ自動車 有価証券報告書 IR情報",
                "earnings": f"{securities_code} OR トヨタ自動車 決算情報 財務情報"
            }
            
            # Google Custom Search APIを使用して検索
            base_url = "https://www.googleapis.com/customsearch/v1"
            
            for category, query in queries.items():
                params = {
                    "key": api_key,
                    "cx": cse_id,
                    "q": query,
                    "num": 10,  # 最大10件の結果を取得
                    "siteSearch": ".jp",  # 日本のサイトに限定
                }
                
                # APIリクエストを実行
                if not self._session:
                    self._session = aiohttp.ClientSession(
                        headers=self.headers,
                        timeout=self.timeout,
                        connector=self.connector
                    )
                
                async with self._session.get(base_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # 検索結果からURLを抽出
                    if "items" in data:
                        for item in data["items"]:
                            url = item.get("link", "")
                            if not url:
                                continue
                                
                            # 企業のドメインに属するURLのみを抽出
                            if any(domain in url.lower() for domain in [
                                "toyota.co.jp",
                                "toyota.com",
                                "global.toyota",
                                "release.tdnet.info",
                                "disclosure.edinet-fsa.go.jp"
                            ]):
                                urls[category] = url
                                break
            
            # URLが取得できなかった場合のフォールバック
            if not urls:
                self._log_warning(f"企業コード {securities_code} のIR URLが見つかりませんでした")
                return {}
            
            return urls
            
        except Exception as e:
            self._log_error(f"IR URL取得エラー: {str(e)}")
            return {}

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
