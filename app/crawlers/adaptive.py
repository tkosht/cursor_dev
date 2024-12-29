"""
LLMを使用した適応型クローラー

HTMLの構造を分析し、動的にセレクタを生成するクローラーです。
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

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
            **kwargs: 基底クラスに渡すキーワード引数
        """
        # AdaptiveCrawler固有のパラメータを抽出
        self.retry_delay = kwargs.pop("retry_delay", 1)
        self.max_concurrent = kwargs.pop("max_concurrent", 5)
        self.cache_ttl = kwargs.pop("cache_ttl", 3600)
        self.max_cache_size = kwargs.pop("max_cache_size", 1000)
        self.default_model = kwargs.pop("default_model", "gemini-2.0-flash-exp")

        # 基底クラスの初期化
        super().__init__(company_code, session=session, **kwargs)

        # AdaptiveCrawler固有の初期化
        self.llm_manager = llm_manager or LLMManager()
        self.retry_count = 0
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        self.logger = logger

        # 並行処理の制御
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

        # キャッシュの設定
        self.cache = {}

    def _generate_cache_key(self, url: str, target_data: Dict[str, str]) -> str:
        """キャッシュキーを生成

        Args:
            url: URL
            target_data: 取得対象データ

        Returns:
            キャッシュキー
        """
        cache_data = {"url": url, "target_data": target_data}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """キャッシュからデータを取得

        Args:
            cache_key: キャッシュキー

        Returns:
            キャッシュデータ（存在しない場合はNone）
        """
        if cache_key not in self.cache:
            return None

        cache_data = self.cache[cache_key]
        if datetime.now() > cache_data["expires_at"]:
            del self.cache[cache_key]
            return None

        return cache_data["data"]

    def _set_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """キャッシュにデータを設定

        Args:
            cache_key: キャッシュキー
            data: キャッシュするデータ
        """
        # キャッシュサイズの制限
        if len(self.cache) >= self.max_cache_size:
            oldest_key = min(
                self.cache.keys(), key=lambda k: self.cache[k]["expires_at"]
            )
            del self.cache[oldest_key]

        self.cache[cache_key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(seconds=self.cache_ttl),
        }

    async def crawl(self, url: str, target_data: Dict[str, str]) -> Dict[str, Any]:
        """クロール処理を実行

        Args:
            url: クロール対象のURL
            target_data: 取得対象データの辞書

        Returns:
            抽出したデータの辞書
        """
        # キャッシュをチェック
        cache_key = self._generate_cache_key(url, target_data)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            self._log_debug(f"キャッシュからデータを取得: {url}")
            return cached_data

        # 並行処理の制御
        async with self.semaphore:
            retry_count = 0
            max_retries = 3
            last_error = None

            while retry_count <= max_retries:
                try:
                    self._log_debug(f"クロール開始: {url} (試行回数: {retry_count + 1})")
                    start_time = time.time()

                    # 1. ページを取得
                    self._log_debug("ページ取得開始")
                    response = await self._make_request(url)
                    html = await response.text()
                    self._log_debug(f"ページ取得完了: {len(html)}バイト")

                    # 2. ページ構造を解析
                    self._log_debug("ページ構造解析開始")
                    soup = BeautifulSoup(html, "html.parser")
                    self._log_debug("ページ構造解析完了")

                    # 3. セレクタを生成
                    self._log_debug("セレクタ生成開始")
                    selectors = await self.llm_manager.generate_selectors(
                        soup, target_data
                    )
                    self._log_debug(f"セレクタ生成完了: {selectors}")

                    # 4. データを抽出
                    self._log_debug("データ抽出開始")
                    extracted_data = await self._extract_data(soup, selectors)
                    self._log_debug(f"データ抽出完了: {extracted_data}")

                    # 5. データを検証
                    self._log_debug("データ検証開始")
                    is_valid = await self.llm_manager.validate_data(
                        extracted_data, target_data
                    )
                    if not is_valid:
                        raise ValueError("データの検証に失敗しました")
                    self._log_debug("データ検証完了")

                    # 6. 処理時間を計測
                    end_time = time.time()
                    processing_time = end_time - start_time
                    self._log_info(f"処理時間: {processing_time:.2f}秒")

                    # キャッシュに保存
                    self._set_to_cache(cache_key, extracted_data)

                    return extracted_data

                except Exception as e:
                    last_error = e
                    error_context = {
                        "url": url,
                        "target_data": target_data,
                        "retry_count": self.retry_count,
                        "error": str(e),
                    }
                    analysis = await self._handle_error(str(e), error_context)

                    if self.retry_count < max_retries and analysis["should_retry"]:
                        self.retry_count += 1
                        backoff = 0.2 * (2 ** (self.retry_count - 1))  # 指数バックオフ
                        self._log_info(f"{backoff}秒後にリトライします (エラー: {str(e)})")
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        break

            if last_error:
                self._log_error(
                    f"最大リトライ回数({max_retries})を超えました。最後のエラー: {str(last_error)}"
                )
                raise last_error

    async def _retry_with_backoff(self) -> None:
        """バックオフ付きリトライ"""
        delay = self.retry_delay * (2**self.retry_count)
        self._log_info(f"{delay}秒後にリトライします")
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
            timeout=self.timeout, headers=self.headers
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
        self, html: str, target_data: Dict[str, str]
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

    async def _extract_data(
        self, soup: BeautifulSoup, selectors: Dict[str, str]
    ) -> Dict[str, Any]:
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
                self._log_debug(f"セレクタ {selector} でデータ抽出開始")
                element = soup.select_one(selector)
                if element:
                    data[key] = element.text.strip()
                    self._log_debug(f"データ抽出成功: {key} = {data[key]}")
                else:
                    self._log_warning(f"セレクタ {selector} でデータが見つかりません")
                    data[key] = None
            except Exception as e:
                self._log_warning(f"データ抽出エラー: {str(e)}")
                data[key] = None

        return data

    async def _validate_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> bool:
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
        self, error: Union[str, Exception], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """エラーを処理し、リトライの判断と対策を提案

        Args:
            error: エラーメッセージまたは例外オブジェクト
            context: エラーが発生した際のコンテキスト情報
                - url: クロール対象のURL
                - target_data: 取得対象データ
                - retry_count: 現在のリトライ回数
                - error: エラーメッセージ

        Returns:
            エラー分析結果の辞書
                - should_retry: リトライすべきかどうか
                - cause: エラーの原因
                - solution: 解決策
        """
        try:
            # エラーメッセージの正規化
            error_message = str(error)

            # エラーログの出力
            self._log_error(f"エラー発生: {error_message}")
            self._log_debug(f"エラーコンテキスト: {json.dumps(context, ensure_ascii=False)}")

            # エラー分析の実行
            analysis_result = await self.llm_manager.analyze_error(
                error_message, context
            )

            # 分析結果のログ出力
            self._log_info(
                f"エラー分析結果:\n"
                f'- 原因: {analysis_result["cause"]}\n'
                f'- 解決策: {analysis_result["solution"]}\n'
                f'- リトライ: {"必要" if analysis_result["should_retry"] else "不要"}'
            )

            # リトライ判断の補助ロジック
            if context["retry_count"] >= self.max_retries:
                analysis_result["should_retry"] = False
                self._log_warning("最大リトライ回数に到達したため、リトライを中止します")

            # エラー情報の記録（3回以上失敗した場合）
            if context["retry_count"] >= 2:
                error_file_path = (
                    f'docs/errors/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.md'
                )
                error_fix_path = (
                    f'docs/fixes/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.md'
                )

                # エラー情報の記録
                with open(error_file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"# エラー情報\n\n"
                        f"## 1. 基本情報\n"
                        f"- 発生日時: {datetime.now().isoformat()}\n"
                        f'- URL: {context["url"]}\n'
                        f'- リトライ回数: {context["retry_count"]}\n\n'
                        f"## 2. エラー詳細\n"
                        f"```\n{error_message}\n```\n\n"
                        f"## 3. コンテキスト\n"
                        f"```json\n{json.dumps(context, indent=2, ensure_ascii=False)}\n```\n"
                    )

                # 修正案の記録
                with open(error_fix_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"# 修正案\n\n"
                        f"## 1. エラー分析\n"
                        f'- 原因: {analysis_result["cause"]}\n'
                        f'- 解決策: {analysis_result["solution"]}\n\n'
                        f"## 2. 対応方針\n"
                        f"1. 即時対応\n"
                        f'   - リトライ: {"必要" if analysis_result["should_retry"] else "不要"}\n'
                        f"2. 恒久対応\n"
                        f"   - 要検討\n"
                    )

            return analysis_result

        except Exception as e:
            self._log_error(f"エラー処理中に例外が発生: {str(e)}")
            return {
                "should_retry": False,
                "cause": "エラー処理に失敗しました",
                "solution": "システム管理者に連絡してください",
            }

    def _log_debug(self, message: str) -> None:
        """デバッグメッセージをログに記録

        Args:
            message: ログメッセージ
        """
        self.logger.debug(message)

    def _log_info(self, message: str) -> None:
        """情報メッセージをログに記録

        Args:
            message: ログメッセージ
        """
        self.logger.info(message)

    def _log_warning(self, message: str) -> None:
        """警告メッセージをログに記録

        Args:
            message: ログメッセージ
        """
        self.logger.warning(message)

    def _log_error(self, message: str) -> None:
        """エラーメッセージをログに記録

        Args:
            message: ログメッセージ
        """
        self.logger.error(message)
