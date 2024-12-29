"""
サイト構造を解析し、企業情報ページを特定するためのモジュール
"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

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

    async def __aenter__(self):
        """
        非同期コンテキストマネージャーのエントリーポイント
        """
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        非同期コンテキストマネージャーの終了処理
        """
        if self._session:
            await self._session.close()
            self._session = None

    async def analyze_site_structure(self, base_url: str) -> Dict[str, Any]:
        """
        サイト構造を解析
        """
        if not self._session:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )

        try:
            logger.info(f"Starting analysis of {base_url}")
            
            # サイトマップの取得
            logger.debug("Fetching sitemap URLs")
            sitemap_urls = await self._get_sitemap_urls(base_url)
            logger.debug(f"Found {len(sitemap_urls)} URLs in sitemap")

            # ナビゲーション構造の解析
            logger.debug("Analyzing navigation structure")
            nav_structure = await self._analyze_navigation(base_url)
            logger.debug(f"Navigation structure analysis complete")

            # 企業情報関連ページの特定
            logger.debug("Identifying relevant pages")
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
            logger.error(f"Error analyzing site structure for {base_url}: {str(e)}")
            raise

    async def _get_sitemap_urls(self, base_url: str) -> List[str]:
        """
        サイトマップからURLリストを取得
        """
        sitemap_urls = []
        try:
            logger.debug(f"Attempting to get sitemap URLs from {base_url}")
            
            # robots.txtからサイトマップの場所を取得
            logger.debug("Checking robots.txt for sitemap")
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
            logger.error(f"Error getting sitemap for {base_url}: {str(e)}")

        return sitemap_urls

    async def _get_sitemap_from_robots(self, base_url: str) -> List[str]:
        """
        robots.txtからサイトマップを取得
        """
        urls = []
        robots_url = urljoin(base_url, "/robots.txt")
        logger.debug(f"Fetching robots.txt from {robots_url}")
        
        response = await self._make_request(robots_url)
        if response and response.status == 200:
            robots_text = await response.text()
            sitemap_location = self._extract_sitemap_location(robots_text)
            if sitemap_location:
                logger.debug(f"Found sitemap location: {sitemap_location}")
                urls.extend(await self._parse_sitemap(sitemap_location))
        else:
            logger.debug("Failed to fetch robots.txt")
        
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
                logger.debug(f"No sitemap at {url}")
        
        return []

    def _extract_sitemap_location(self, robots_text: str) -> Optional[str]:
        """
        robots.txtからサイトマップの場所を抽出

        Args:
            robots_text: robots.txtの内容

        Returns:
            サイトマップのURL（見つからない場合はNone）
        """
        for line in robots_text.split("\n"):
            if line.lower().startswith("sitemap:"):
                return line.split(":", 1)[1].strip()
        return None

    async def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        サイトマップをパースしてURLリストを取得
        """
        urls = []
        logger.debug(f"Parsing sitemap at {sitemap_url}")
        
        response = await self._make_request(sitemap_url)
        if response and response.status == 200:
            try:
                content = await response.text()
                root = ET.fromstring(content)
                
                # 名前空間の取得
                ns = {"sm": root.tag.split("}")[0][1:]} if "}" in root.tag else ""
                
                # URLの抽出
                if ns:
                    locations = root.findall(".//sm:loc", ns)
                else:
                    locations = root.findall(".//loc")
                
                urls.extend([loc.text for loc in locations if loc.text])
                logger.debug(f"Found {len(urls)} URLs in sitemap")
                
            except ET.ParseError as e:
                logger.error(f"Error parsing sitemap XML: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing sitemap: {str(e)}")
        else:
            logger.debug("Failed to fetch sitemap")
        
        return urls

    async def _analyze_navigation(self, base_url: str) -> Dict[str, List[str]]:
        """
        サイトのナビゲーション構造を解析
        """
        nav_structure = {"main_nav": [], "footer_nav": [], "other_nav": []}
        logger.debug(f"Analyzing navigation at {base_url}")
        
        response = await self._make_request(base_url)
        if response and response.status == 200:
            try:
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                # メインナビゲーションの解析
                main_nav = soup.find("nav")
                if main_nav:
                    nav_structure["main_nav"] = [
                        urljoin(base_url, a["href"])
                        for a in main_nav.find_all("a", href=True)
                    ]
                    logger.debug(f"Found {len(nav_structure['main_nav'])} main navigation links")
                
                # フッターナビゲーションの解析
                footer = soup.find("footer")
                if footer:
                    nav_structure["footer_nav"] = [
                        urljoin(base_url, a["href"])
                        for a in footer.find_all("a", href=True)
                    ]
                    logger.debug(f"Found {len(nav_structure['footer_nav'])} footer navigation links")
                
                # その他のナビゲーション要素の解析
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
                logger.error(f"Error analyzing navigation: {str(e)}")
        else:
            logger.debug("Failed to fetch page for navigation analysis")
        
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
                    'page_type': ページタイプ
                },
                ...
            ]
        """
        relevant_pages = []

        # 評価対象URLの収集
        target_urls = set()
        target_urls.update(sitemap_urls)
        for nav_urls in nav_structure.values():
            target_urls.update(nav_urls)

        # URLのフィルタリング
        base_domain = urlparse(base_url).netloc
        filtered_urls = [
            url
            for url in target_urls
            if urlparse(url).netloc == base_domain
            and self._is_potentially_relevant_url(url)
        ]

        # 各URLの評価
        for url in filtered_urls:
            try:
                async with self._session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        relevance_score = await self.evaluate_page(url, content)

                        if relevance_score > 0.5:  # 関連性の閾値
                            relevant_pages.append(
                                {
                                    "url": url,
                                    "relevance_score": relevance_score,
                                    "page_type": self._determine_page_type(url),
                                }
                            )

            except Exception as e:
                logger.error(f"Error evaluating page {url}: {str(e)}")

        # スコアの降順でソート
        relevant_pages.sort(key=lambda x: x["relevance_score"], reverse=True)
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

    async def _make_request(self, url: str, method: str = "GET") -> Optional[aiohttp.ClientResponse]:
        """
        リトライ機能付きのHTTPリクエスト

        Args:
            url: リクエスト先URL
            method: HTTPメソッド

        Returns:
            レスポンス（失敗時はNone）
        """
        for attempt in range(MAX_RETRIES):
            try:
                if attempt > 0:
                    await asyncio.sleep(REQUEST_INTERVAL * (2 ** attempt))  # 指数バックオフ
                
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1}/{MAX_RETRIES})")
                response = await self._session.request(method, url)
                
                if response.status == 429:  # レート制限
                    logger.warning(f"Rate limit hit for {url}, waiting before retry")
                    continue
                
                return response

            except asyncio.TimeoutError:
                logger.warning(f"Timeout accessing {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            except aiohttp.ClientError as e:
                logger.warning(f"Error accessing {url}: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            await asyncio.sleep(REQUEST_INTERVAL)  # 次のリトライまで待機
        
        logger.error(f"Failed to access {url} after {MAX_RETRIES} attempts")
        return None
