"""
企業情報収集のためのURLコレクター統合テスト

実際の企業サイトからIR情報や会社情報のURLを収集するテストを実施します。
複数の企業サイトでテストを行い、クローラーの汎用性を担保します。
"""

import asyncio
import logging
from typing import Dict, List, Optional

import pytest
from dotenv import load_dotenv

from app.crawlers.adaptive_url_collector import AdaptiveURLCollector
from app.llm.constants import LLMConstants
from app.llm.manager import LLMConfig, LLMManager

# .envファイルを読み込む
load_dotenv()

# テガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# テスト設定
TEST_TIMEOUT = 60.0  # テストのタイムアウト時間を1分に短縮
REQUEST_TIMEOUT = 20.0  # リクエストのタイムアウト時間を20秒に短縮
MAX_RETRIES = 2  # 最大リトライ回数を2回に削減
RETRY_DELAY = 2.0  # リトライ間隔を2秒に短縮

# テスト対象の企業サイト定義を厳選（処理時間短縮のため）
TARGET_COMPANIES = [
    {
        "name": "トヨタ自動車",
        "domain": "toyota.co.jp",
        "url": "https://www.toyota.co.jp/jpn/investors/"
    },
    {
        "name": "ソニーグループ",
        "domain": "sony.com",
        "url": "https://www.sony.com/ja/SonyInfo/IR/"
    }
]


class URLCollectorTestHelper:
    """URLコレクターのテストヘルパー"""

    @staticmethod
    def verify_urls(
        urls: List[str],
        company_name: str,
        target_paths: Optional[List[str]] = None,
        path_type: str = ""
    ) -> None:
        """URLの検証を行う

        Args:
            urls: 検証対象のURL
            company_name: 企業名
            target_paths: 検索対象のパス
            path_type: パスの種類（エラーメッセージ用）
        """
        # 基本的な検証
        assert len(urls) > 0, f"{company_name}: URLが収集できませんでした"
        assert all(url.startswith(("http://", "https://")) for url in urls), \
            f"{company_name}: 無効なURLが含まれています"

        # パスの検証（target_pathsが指定された場合のみ）
        if target_paths:
            found_paths = [
                url for url in urls 
                if any(path in url.lower() for path in target_paths)
            ]
            assert len(found_paths) > 0, \
                f"{company_name}: {path_type}関連のURLが見つかりませんでした"
            
    @staticmethod
    def create_collector_with_domains(
        collector_factory,
        domains: List[str]
    ) -> AdaptiveURLCollector:
        """ドメインを指定してコレクターを作成

        Args:
            collector_factory: コレクターのファクトリ関数
            domains: 許可するドメインのリスト

        Returns:
            AdaptiveURLCollector: 作成されたコレクター
        """
        return collector_factory(domains)

    @staticmethod
    async def retry_with_backoff(
        func,
        *args,
        max_retries: int = MAX_RETRIES,
        retry_delay: float = RETRY_DELAY,
        **kwargs
    ):
        """バックオフ付きリトライ

        Args:
            func: 実行する関数
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
            *args: 関数の位置引数
            **kwargs: 関数のキーワード引数

        Returns:
            Any: 関数の実行結果

        Raises:
            Exception: すべてのリトライが失敗した場合
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"試行 {attempt + 1}/{max_retries} "
                    f"(関数: {func.__name__}, 引数: {args}, キーワード引数: {kwargs})"
                )
                result = await func(*args, **kwargs)
                logger.info(f"試行 {attempt + 1} が成功しました")
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    f"試行 {attempt + 1} が失敗: {str(e)}, "
                    f"待機時間: {retry_delay * (2 ** attempt)}秒"
                )
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)  # 指数バックオフ
                    await asyncio.sleep(delay)
                continue
        logger.error(f"すべての試行が失敗: {str(last_error)}")
        raise last_error


@pytest.fixture
def collector_factory():
    """URLCollectorのファクトリ関数"""
    def _create_collector(domains: List[str]) -> AdaptiveURLCollector:
        llm_config = LLMConfig(
            model_name="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=1000,
            timeout=REQUEST_TIMEOUT
        )
        llm_manager = LLMManager(config=llm_config)
        
        return AdaptiveURLCollector(
            llm_manager=llm_manager,
            max_concurrent_requests=3,
            request_timeout=REQUEST_TIMEOUT,
            max_retries=MAX_RETRIES,
            allowed_domains=domains + ["release.tdnet.info"]
        )
    return _create_collector


@pytest.fixture
def test_helper():
    """テストヘルパーのフィクスチャ"""
    return URLCollectorTestHelper


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_ir_urls_from_navigation(
    collector_factory,
    test_helper,
    company: Dict
):
    """各企業サイトのナビゲーションからIR情報URLを収集"""
    collector = test_helper.create_collector_with_domains(
        collector_factory,
        [company["domain"]]
    )
    
    urls = await test_helper.retry_with_backoff(
        collector.collect_urls_adaptively,
        company["url"],
        {"target_type": "ir_info"}
    )
    test_helper.verify_urls(
        urls=urls,
        company_name=company["name"],
        target_paths=LLMConstants.TARGET_PATHS["ir_info"],
        path_type="IR"
    )


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_company_info_urls(
    collector_factory,
    test_helper,
    company: Dict
):
    """各企業サイトから会社情報URLを収集"""
    collector = test_helper.create_collector_with_domains(
        collector_factory,
        [company["domain"]]
    )
    
    urls = await test_helper.retry_with_backoff(
        collector.collect_urls_adaptively,
        company["url"],
        {"target_type": "company_info"}
    )
    test_helper.verify_urls(
        urls=urls,
        company_name=company["name"],
        target_paths=LLMConstants.TARGET_PATHS["company_info"],
        path_type="会社情報"
    )


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_financial_info_urls(
    collector_factory,
    test_helper,
    company: Dict
):
    """各企業サイトから財務情報URLを収集"""
    collector = test_helper.create_collector_with_domains(
        collector_factory,
        [company["domain"]]
    )
    
    urls = await test_helper.retry_with_backoff(
        collector.collect_urls_adaptively,
        company["url"],
        {"target_type": "financial_info"}
    )
    test_helper.verify_urls(
        urls=urls,
        company_name=company["name"],
        target_paths=LLMConstants.TARGET_PATHS["financial_info"],
        path_type="財務情報"
    )


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_urls_with_error_recovery(
    collector_factory,
    test_helper,
    company: Dict
):
    """エラー発生時のリカバリー機能をテスト"""
    collector = test_helper.create_collector_with_domains(
        collector_factory,
        [company["domain"]]
    )
    
    # エラーを発生させるためのコンテキスト
    error_context = {
        "target_type": "invalid_type",
        "force_error": True
    }
    
    # エラー発生後のリカバリーを確認
    urls = await test_helper.retry_with_backoff(
        collector.collect_urls_adaptively,
        company["url"],
        error_context
    )
    
    # リカバリー後のURLが正しく収集できているか確認
    test_helper.verify_urls(
        urls=urls,
        company_name=company["name"],
        target_paths=LLMConstants.TARGET_PATHS["ir_info"],
        path_type="IR"
    )


@pytest.mark.asyncio
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_cross_domain_collection(
    collector_factory,
    test_helper,
    company: Dict
):
    """関連ドメイン間のリンク収集テスト"""
    domains = [
        company["domain"],
        f"ir.{company['domain']}",
        f"www.{company['domain']}"
    ]
    collector = test_helper.create_collector_with_domains(
        collector_factory,
        domains
    )
    
    # メインサイトとIRサイトの両方からリンクを収集
    main_urls = await test_helper.retry_with_backoff(
        collector.collect_urls_adaptively,
        company["url"],
        context={"target_type": "ir_info"}
    )
    
    # IRサイトが存在する場合は、そこからもリンクを収集
    ir_url = f"https://ir.{company['domain']}"
    try:
        ir_urls = await test_helper.retry_with_backoff(
            collector.collect_urls_adaptively,
            ir_url,
            context={"target_type": "ir_info"}
        )
        all_urls = main_urls + ir_urls
    except Exception:
        all_urls = main_urls
    
    # URLの検証
    test_helper.verify_urls(
        urls=all_urls,
        company_name=company["name"]
    )
    
    # ドメインの検証
    main_domain_urls = [url for url in all_urls if company["domain"] in url]
    assert len(main_domain_urls) > 0, \
        f"{company['name']}: メインドメインのURLが見つかりませんでした" 

"""実際のURLに対する統合テスト"""

import asyncio
import logging
from typing import Dict, List

import pytest

from app.crawlers.adaptive_url_collector import AdaptiveURLCollector
from app.llm.manager import LLMManager

logger = logging.getLogger(__name__)

# テスト対象のURL（実在するIRサイト）
TEST_URLS = [
    "https://www.toyota.co.jp/jpn/investors/",
    "https://www.sony.com/ja/SonyInfo/IR/",
    "https://www.nintendo.co.jp/ir/",
    "https://www.mitsubishicorp.com/jp/ja/ir/",
    "https://www.panasonic.com/jp/corporate/ir.html"
]

@pytest.fixture
async def url_collector():
    """URLコレクターのフィクスチャ"""
    collector = AdaptiveURLCollector(
        max_concurrent_requests=1,  # 同時リクエストを制限
        request_timeout=30.0,
        max_retries=2,
        retry_delay=5.0
    )
    yield collector
    await collector.close()

@pytest.mark.asyncio
async def test_collect_ir_urls(url_collector):
    """IR情報のURL収集テスト"""
    for url in TEST_URLS:
        try:
            # IR情報のコンテキストでURL収集
            urls = await url_collector.collect_urls_adaptively(
                url,
                {"target_type": "ir_info"}
            )

            # 基本的な検証
            assert urls, f"URLが収集できませんでした: {url}"
            assert isinstance(urls, list), "戻り値はリストである必要があります"
            assert all(isinstance(u, str) for u in urls), "すべての要素がURLである必要があります"

            # IR関連URLの特徴を確認
            ir_keywords = ["ir", "investor", "financial", "earnings", "results"]
            has_ir_urls = any(
                any(kw in u.lower() for kw in ir_keywords)
                for u in urls
            )
            assert has_ir_urls, f"IR関連のURLが含まれていません: {url}"

            # アクセス間隔を確保
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"テスト失敗 - URL: {url}, エラー: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_adaptive_pattern_generation(url_collector):
    """パターン生成の適応性テスト"""
    url = TEST_URLS[0]  # 1つのサイトで十分
    context = {"target_type": "ir_info"}

    try:
        # 1回目の収集
        urls_first = await url_collector.collect_urls_adaptively(url, context)
        assert urls_first, "1回目のURL収集に失敗"

        # パターンが保存されていることを確認
        assert url in url_collector.extraction_patterns
        patterns = url_collector.extraction_patterns[url]
        assert patterns, "パターンが保存されていません"

        # アクセス間隔を確保
        await asyncio.sleep(5)

        # 2回目の収集（保存されたパターンを使用）
        urls_second = await url_collector.collect_urls_adaptively(url, context)
        assert urls_second, "2回目のURL収集に失敗"

        # 結果を比較
        common_urls = set(urls_first) & set(urls_second)
        assert common_urls, "2回の収集で共通のURLが見つかりません"

    except Exception as e:
        logger.error(f"テスト失敗 - URL: {url}, エラー: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_error_handling(url_collector):
    """エラーハンドリングテスト"""
    invalid_url = "https://invalid.example.com/ir"
    context = {"target_type": "ir_info"}

    try:
        urls = await url_collector.collect_urls_adaptively(invalid_url, context)
        assert not urls, "無効なURLからURLが収集されました"
    except Exception as e:
        logger.info(f"期待通りのエラー発生: {str(e)}")

@pytest.mark.asyncio
async def test_domain_restriction(url_collector):
    """ドメイン制限テスト"""
    url = TEST_URLS[0]
    allowed_domains = ["toyota.co.jp"]
    url_collector.allowed_domains = set(allowed_domains)

    try:
        urls = await url_collector.collect_urls_adaptively(
            url,
            {"target_type": "ir_info"}
        )
        assert urls, "URLが収集できませんでした"

        # すべてのURLが許可されたドメインに属することを確認
        for collected_url in urls:
            assert any(
                domain in collected_url
                for domain in allowed_domains
            ), f"許可されていないドメインのURL: {collected_url}"

    except Exception as e:
        logger.error(f"テスト失敗 - URL: {url}, エラー: {str(e)}")
        raise 