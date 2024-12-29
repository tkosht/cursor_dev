"""
サイト構造を解析し、企業情報ページを特定するためのモジュール
"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from app.llm.manager import LLMManager

# ログレベルを DEBUG に設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# コンソールハンドラを追加
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# 定数
DEFAULT_TIMEOUT = 30  # 秒
REQUEST_INTERVAL = 1.0  # 秒
MAX_RETRIES = 3


def _is_navigation_element(class_name: Optional[str]) -> bool:
    """
    クラス名がナビゲーション要素かどうかを判定

    Args:
        class_name: クラス名

    Returns:
        ナビゲーション要素かどうか
    """
    if not class_name:
        return False
    return "nav" in class_name.lower() or "menu" in class_name.lower()


def _is_main_content_element(class_name: Optional[str]) -> bool:
    """
    クラス名がメインコンテンツ要素かどうかを判定

    Args:
        class_name: クラス名

    Returns:
        メインコンテンツ要素かどうか
    """
    if not class_name:
        return False
    return "main" in class_name.lower() or "content" in class_name.lower()


class SiteAnalyzer:
    """
    ウェブサイトの構造を解析し、企業情報ページを特定するクラス
    """

    def __init__(self, llm_manager: LLMManager):
        """
        初期化

        Args:
            llm_manager: LLMManagerインスタンス
        """
        self.llm_manager = llm_manager
        self._session: Optional[aiohttp.ClientSession] = None
        logger.debug("SiteAnalyzer initialized with LLMManager")

    async def __aenter__(self):
        """
        非同期コンテキストマネージャーのエントリーポイント
        """
        logger.debug("Creating aiohttp ClientSession")
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        # HTTP/1.1とUser-Agentを設定
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (compatible; CompanyCrawler/1.0; +https://example.com/bot)"
            },
            version="1.1"  # HTTP/1.1を強制
        )
        logger.debug("aiohttp ClientSession created with HTTP/1.1 and User-Agent")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        非同期コンテキストマネージャーの終了処理
        """
        if self._session:
            logger.debug("Closing aiohttp ClientSession")
            await self._session.close()
            self._session = None
            logger.debug("aiohttp ClientSession closed")

    async def analyze_site_structure(self, base_url: str) -> Dict[str, Any]:
        """
        サイト構造を解析
        """
        if not self._session:
            logger.error("Session not initialized. Use 'async with' context manager.")
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )

        try:
            logger.info(f"Starting analysis of {base_url}")
            
            # サイトマップの取得
            logger.debug("Starting to fetch sitemap URLs")
            sitemap_urls = await self._get_sitemap_urls(base_url)
            logger.debug(f"Found {len(sitemap_urls)} URLs in sitemap")

            # ナビゲーション構造の解析
            logger.debug("Starting navigation structure analysis")
            nav_structure = await self._analyze_navigation(base_url)
            logger.debug("Navigation structure analysis completed")

            # 企業情報関連ページの特定
            logger.debug("Starting to identify relevant pages")
            relevant_pages = await self._identify_relevant_pages(
                base_url, sitemap_urls, nav_structure
            )
            logger.debug(f"Found {len(relevant_pages)} relevant pages")

            return {
                "sitemap": sitemap_urls,
                "navigation": nav_structure,
                "relevant_pages": relevant_pages,
            }

        except Exception as e:
            logger.error(f"Error analyzing site structure for {base_url}: {str(e)}", exc_info=True)
            raise

    async def _get_sitemap_urls(self, base_url: str) -> List[str]:
        """
        サイトマップからURLリストを取得
        """
        sitemap_urls = []
        try:
            logger.debug(f"Starting to get sitemap URLs from {base_url}")
            
            # robots.txtからサイトマップの場所を取得
            logger.debug("Checking robots.txt for sitemap location")
            sitemap_urls.extend(await self._get_sitemap_from_robots(base_url))
            logger.debug(f"Found {len(sitemap_urls)} URLs from robots.txt")

            # 一般的なサイトマップの場所もチェック
            if not sitemap_urls:
                logger.debug("No sitemap in robots.txt, checking common locations")
                sitemap_urls.extend(
                    await self._get_sitemap_from_common_locations(base_url)
                )
                logger.debug(f"Found {len(sitemap_urls)} URLs from common locations")

        except Exception as e:
            logger.error(f"Error getting sitemap for {base_url}: {str(e)}", exc_info=True)

        return sitemap_urls

    async def _get_sitemap_from_robots(self, base_url: str) -> List[str]:
        """
        robots.txtからサイトマップを取得
        取得に失敗した場合は空のリストを返す
        """
        urls = []
        robots_url = urljoin(base_url, "/robots.txt")
        logger.info(f"Attempting to fetch robots.txt from {robots_url}")
        
        try:
            response = await self._make_request(robots_url)
            if response and response.status == 200:
                logger.info("Successfully fetched robots.txt")
                robots_text = await response.text()
                sitemap_location = self._extract_sitemap_location(robots_text)
                if sitemap_location:
                    logger.info(f"Found sitemap location in robots.txt: {sitemap_location}")
                    urls.extend(await self._parse_sitemap(sitemap_location))
                else:
                    logger.info("No sitemap location found in robots.txt")
            else:
                logger.info(
                    f"Failed to fetch robots.txt (status: {response.status if response else 'No response'}), "
                    "skipping..."
                )
        except Exception as e:
            logger.info(f"Error accessing robots.txt: {str(e)}, skipping...")
        
        return urls

    async def _get_sitemap_from_common_locations(self, base_url: str) -> List[str]:
        """
        一般的な場所からサイトマップを取得
        """
        common_locations = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap/",
        ]
        for location in common_locations:
            url = urljoin(base_url, location)
            logger.debug(f"Checking sitemap at {url}")
            
            response = await self._make_request(url)
            if response and response.status == 200:
                logger.debug(f"Found sitemap at {url}")
                return await self._parse_sitemap(url)
            else:
                logger.debug(f"No sitemap at {url}: {response.status if response else 'No response'}")
        
        return []

    def _extract_sitemap_location(self, robots_text: str) -> Optional[str]:
        """
        robots.txtからサイトマップの場所を抽出

        Args:
            robots_text: robots.txtの内容

        Returns:
            サイトマップのURL（見つからない場合はNone）
        """
        logger.debug("Extracting sitemap location from robots.txt")
        for line in robots_text.split("\n"):
            if line.lower().startswith("sitemap:"):
                location = line.split(":", 1)[1].strip()
                logger.debug(f"Found sitemap location: {location}")
                return location
        logger.debug("No sitemap location found in robots.txt")
        return None

    async def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        サイトマップをパースしてURLリストを取得
        """
        urls = []
        logger.debug(f"Starting to parse sitemap at {sitemap_url}")
        
        response = await self._make_request(sitemap_url)
        if response and response.status == 200:
            try:
                logger.debug("Successfully fetched sitemap content")
                content = await response.text()
                root = ET.fromstring(content)
                
                # 名前空間の取得
                ns = {"sm": root.tag.split("}")[0][1:]} if "}" in root.tag else ""
                logger.debug(f"Sitemap namespace: {ns}")
                
                # URLの抽出
                if ns:
                    locations = root.findall(".//sm:loc", ns)
                else:
                    locations = root.findall(".//loc")
                
                urls.extend([loc.text for loc in locations if loc.text])
                logger.debug(f"Extracted {len(urls)} URLs from sitemap")
                
            except ET.ParseError as e:
                logger.error(f"Error parsing sitemap XML: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Error processing sitemap: {str(e)}", exc_info=True)
        else:
            logger.debug(f"Failed to fetch sitemap: {response.status if response else 'No response'}")
        
        return urls

    async def _analyze_navigation(self, base_url: str) -> Dict[str, List[str]]:
        """
        サイトのナビゲーション構造を解析
        """
        nav_structure = {"main_nav": [], "footer_nav": [], "other_nav": []}
        logger.debug(f"Starting navigation analysis for {base_url}")
        
        response = await self._make_request(base_url)
        if response and response.status == 200:
            try:
                logger.debug("Successfully fetched base page")
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                # メインナビゲーションの解析
                logger.debug("Analyzing main navigation")
                main_nav = soup.find("nav")
                if main_nav:
                    nav_structure["main_nav"] = [
                        urljoin(base_url, a["href"])
                        for a in main_nav.find_all("a", href=True)
                    ]
                    logger.debug(f"Found {len(nav_structure['main_nav'])} main navigation links")
                
                # フッターナビゲーションの解析
                logger.debug("Analyzing footer navigation")
                footer = soup.find("footer")
                if footer:
                    nav_structure["footer_nav"] = [
                        urljoin(base_url, a["href"])
                        for a in footer.find_all("a", href=True)
                    ]
                    logger.debug(f"Found {len(nav_structure['footer_nav'])} footer navigation links")
                
                # その他のナビゲーション要素の解析
                logger.debug("Analyzing other navigation elements")
                other_navs = soup.find_all(
                    ["nav", "ul", "div"], class_=_is_navigation_element
                )
                for nav in other_navs:
                    nav_structure["other_nav"].extend([
                        urljoin(base_url, a["href"])
                        for a in nav.find_all("a", href=True)
                    ])
                logger.debug(f"Found {len(nav_structure['other_nav'])} other navigation links")
                
            except Exception as e:
                logger.error(f"Error analyzing navigation: {str(e)}", exc_info=True)
        else:
            logger.debug(f"Failed to fetch base page: {response.status if response else 'No response'}")
        
        return nav_structure

    async def _identify_relevant_pages(
        self,
        base_url: str,
        sitemap_urls: List[str],
        nav_structure: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """
        企業情報関連ページを特定

        Args:
            base_url: サイトのベースURL
            sitemap_urls: サイトマップから取得したURL
            nav_structure: ナビゲーション構造

        Returns:
            関連ページ情報のリスト
            [
                {
                    'url': ページのURL,
                    'relevance_score': 関連性スコア,
                    'evaluation_reason': 評価理由,
                    'page_type': ページタイプ
                },
                ...
            ]
        """
        logger.debug(f"Starting to identify relevant pages for {base_url}")
        relevant_pages = []

        # 評価対象URLの収集と重複除去
        target_urls = set()
        target_urls.update(sitemap_urls)
        for nav_urls in nav_structure.values():
            target_urls.update(nav_urls)
        logger.debug(f"Collected {len(target_urls)} total URLs to evaluate")

        # 外部ドメインの除外
        base_domain = urlparse(base_url).netloc
        filtered_urls = [
            url for url in target_urls
            if urlparse(url).netloc == base_domain
        ]
        logger.debug(f"Filtered down to {len(filtered_urls)} URLs after domain check")

        # 同時実行数の制限
        semaphore = asyncio.Semaphore(5)  # 最大5件の同時実行

        async def evaluate_url(url: str) -> Optional[Dict[str, Any]]:
            """
            URLの評価を実行
            """
            async with semaphore:
                try:
                    # URLの構造解析
                    parsed_url = urlparse(url)
                    path_components = parsed_url.path.strip("/").split("/")
                    
                    # LLMによるURL評価
                    url_eval_result = await self.llm_manager.evaluate_url_relevance(
                        url=url,
                        path_components=path_components,
                        query_params=parse_qs(parsed_url.query)
                    )
                    
                    if not url_eval_result:
                        return None
                    
                    relevance_score = url_eval_result.get("relevance_score", 0.0)
                    if relevance_score > 0.4:  # 間接的関連以上を収集
                        return {
                            "url": url,
                            "relevance_score": relevance_score,
                            "evaluation_reason": url_eval_result.get("reason", ""),
                            "page_type": url_eval_result.get("category", "other")
                        }
                    
                except Exception as e:
                    logger.error(f"Error evaluating URL {url}: {str(e)}", exc_info=True)
                
                return None

        # 並列評価の実行
        tasks = [evaluate_url(url) for url in filtered_urls]
        results = await asyncio.gather(*tasks)
        
        # 有効な結果のみを抽出
        relevant_pages = [page for page in results if page]
        
        # スコアの降順でソート
        relevant_pages.sort(key=lambda x: x["relevance_score"], reverse=True)
        logger.debug(f"Final count of relevant pages: {len(relevant_pages)}")
        
        return relevant_pages

    def _is_potentially_relevant_url(self, url: str) -> bool:
        """
        URLが企業情報ページである可能性を判定

        Args:
            url: 評価対象のURL

        Returns:
            企業情報ページの可能性があるかどうか
        """
        relevant_patterns = [
            "/company/",
            "/about/",
            "/corporate/",
            "/profile/",
            "/info/",
            "/about-us/",
            "/who-we-are/",
            "/overview/",
        ]

        path = urlparse(url).path.lower()
        return any(pattern in path for pattern in relevant_patterns)

    def _determine_page_type(self, url: str) -> str:
        """
        URLからページタイプを判定

        Args:
            url: 評価対象のURL

        Returns:
            ページタイプ
        """
        path = urlparse(url).path.lower()

        if "/company/" in path:
            return "company_profile"
        elif "/about/" in path:
            return "about_us"
        elif "/corporate/" in path:
            return "corporate_info"
        elif "/profile/" in path:
            return "company_profile"
        elif "/ir/" in path:
            return "investor_relations"
        else:
            return "other"

    async def evaluate_page(self, url: str, content: str) -> float:
        """
        ページの関連性を評価

        Args:
            url: ページのURL
            content: ページのコンテンツ

        Returns:
            関連性スコア（0.0-1.0）
        """
        try:
            # HTMLの解析
            soup = BeautifulSoup(content, "html.parser")

            # メタデータの抽出
            title = soup.title.string if soup.title else ""
            meta_description = ""
            meta_keywords = ""

            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get("content", "")

            meta_keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords_tag:
                meta_keywords = meta_keywords_tag.get("content", "")

            # メインコンテンツの抽出
            main_content = ""
            main_tags = soup.find_all(
                ["main", "article", "div"], class_=_is_main_content_element
            )
            if main_tags:
                main_content = " ".join([tag.get_text() for tag in main_tags])
            else:
                main_content = soup.get_text()

            # LLMによる評価
            evaluation_result = await self.llm_manager.evaluate_page_relevance(
                url=url,
                title=title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                main_content=main_content[:1000],  # コンテンツは最初の1000文字のみ使用
            )

            return float(evaluation_result)

        except Exception as e:
            logger.error(f"Error evaluating page {url}: {str(e)}")
            return 0.0

    async def _handle_response(
        self,
        response: aiohttp.ClientResponse,
        url: str,
        retry_count: int
    ) -> tuple[Optional[aiohttp.ClientResponse], bool, float]:
        """
        レスポンスを処理し、リトライが必要かどうかを判断

        Args:
            response: HTTPレスポンス
            url: リクエスト先URL
            retry_count: 現在のリトライ回数

        Returns:
            (レスポンス, リトライ必要か, 待機時間)のタプル
        """
        if response.status == 429:  # レート制限
            retry_after = response.headers.get("Retry-After", REQUEST_INTERVAL)
            wait_time = float(retry_after) if retry_after.isdigit() else REQUEST_INTERVAL
            logger.warning(f"Rate limited. Waiting {wait_time} seconds")
            return None, True, wait_time
        
        elif response.status >= 500:  # サーバーエラー
            logger.warning(f"Server error {response.status} for {url}")
            return None, True, REQUEST_INTERVAL * (2 ** retry_count)
        
        elif response.status == 404:  # Not Found
            logger.info(f"Resource not found: {url}")
            return None, False, 0
        
        elif response.status >= 400:  # その他のクライアントエラー
            logger.warning(f"Client error {response.status} for {url}")
            return None, False, 0
        
        return response, False, 0

    async def _make_request(self, url: str, method: str = "GET") -> Optional[aiohttp.ClientResponse]:
        """
        HTTPリクエストを実行（リトライロジック付き）

        Args:
            url: リクエスト先URL
            method: HTTPメソッド（デフォルトはGET）

        Returns:
            レスポンス（失敗時はNone）
        """
        if not self._session:
            logger.error("Session not initialized")
            return None

        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # 指数バックオフによる待機（初回は待機なし）
                if retry_count > 0:
                    wait_time = REQUEST_INTERVAL * (2 ** (retry_count - 1))
                    logger.debug(f"Waiting {wait_time} seconds before retry {retry_count + 1}")
                    await asyncio.sleep(wait_time)

                logger.debug(f"Making {method} request to {url} (attempt {retry_count + 1}/{MAX_RETRIES})")
                response = await self._session.request(method, url)
                
                # レスポンスの処理
                result, should_retry, wait_time = await self._handle_response(response, url, retry_count)
                if should_retry:
                    await asyncio.sleep(wait_time)
                    retry_count += 1
                    continue
                return result

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Request failed: {str(e)}")
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    logger.error(f"Max retries ({MAX_RETRIES}) exceeded for {url}")
                    return None
                continue

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                return None

        return None
