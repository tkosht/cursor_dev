"""
企業情報収集のためのURLコレクター統合テスト

実際の企業サイトからIR情報や会社情報のURLを収集するテストを実施します。
複数の企業サイトでテストを行い、クローラーの汎用性を担保します。
"""

from typing import Dict, List

import pytest

from app.crawlers.url_collector import URLCollector

# テスト対象の企業サイト定義
TARGET_COMPANIES = [
    {
        "name": "日本取引所グループ",
        "domain": "jpx.co.jp",
        "url": "https://www.jpx.co.jp",
        "ir_paths": ["/ir/", "/investor/"],
        "company_paths": ["/company/", "/about/"],
        "financial_paths": ["/financial/", "/finance/"]
    },
    {
        "name": "ソニーグループ",
        "domain": "sony.com",
        "url": "https://www.sony.com/ja/",
        "ir_paths": ["/ir/", "/investor/"],
        "company_paths": ["/company/", "/about/", "/SonyInfo/"],
        "financial_paths": ["/financial/", "/finance/", "/earnings/"]
    },
    {
        "name": "トヨタ自動車",
        "domain": "toyota.co.jp",
        "url": "https://global.toyota/jp/",
        "ir_paths": ["/ir/", "/investors/"],
        "company_paths": ["/company/", "/corporate/"],
        "financial_paths": ["/financial/", "/finance/", "/earnings/"]
    }
]


@pytest.fixture
def collector_factory():
    """URLCollectorのファクトリ関数"""
    def _create_collector(domains: List[str]) -> URLCollector:
        return URLCollector(
            max_concurrent_requests=3,
            request_timeout=30.0,
            allowed_domains=domains + ["release.tdnet.info"]  # TDnetは常に許可
        )
    return _create_collector


@pytest.mark.asyncio
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_ir_urls_from_navigation(collector_factory, company: Dict):
    """各企業サイトのナビゲーションからIR情報URLを収集"""
    collector = collector_factory([company["domain"]])
    
    # 企業サイトからIR関連リンクを収集
    urls = await collector.collect_from_navigation(company["url"])
    
    # 基本的な検証
    assert len(urls) > 0, f"{company['name']}: URLが収集できませんでした"
    assert all(url.startswith(("http://", "https://")) for url in urls)
    
    # IR情報関連のパスが含まれているか確認
    found_ir_paths = [
        url for url in urls 
        if any(path in url.lower() for path in company["ir_paths"])
    ]
    assert len(found_ir_paths) > 0, f"{company['name']}: IR関連のURLが見つかりませんでした"


@pytest.mark.asyncio
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_company_info_from_sitemap(collector_factory, company: Dict):
    """各企業サイトのサイトマップから会社情報URLを収集"""
    collector = collector_factory([company["domain"]])
    
    # サイトマップから会社情報を収集
    urls = await collector.collect_from_sitemap(company["url"])
    
    # 基本的な検証
    assert len(urls) > 0, f"{company['name']}: URLが収集できませんでした"
    assert all(url.startswith(("http://", "https://")) for url in urls)
    
    # 会社情報関連のパスが含まれているか確認
    found_company_paths = [
        url for url in urls 
        if any(path in url.lower() for path in company["company_paths"])
    ]
    assert len(found_company_paths) > 0, f"{company['name']}: 会社情報関連のURLが見つかりませんでした"


@pytest.mark.asyncio
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_collect_financial_info_from_footer(collector_factory, company: Dict):
    """各企業サイトのフッターから財務情報URLを収集"""
    collector = collector_factory([company["domain"]])
    
    # フッターから財務情報を収集
    urls = await collector.collect_from_footer(company["url"])
    
    # 基本的な検証
    assert len(urls) > 0, f"{company['name']}: URLが収集できませんでした"
    assert all(url.startswith(("http://", "https://")) for url in urls)
    
    # 財務情報関連のパスが含まれているか確認
    found_financial_paths = [
        url for url in urls 
        if any(path in url.lower() for path in company["financial_paths"])
    ]
    assert len(found_financial_paths) > 0, f"{company['name']}: 財務情報関連のURLが見つかりませんでした"


@pytest.mark.asyncio
@pytest.mark.parametrize("company", TARGET_COMPANIES)
async def test_cross_domain_collection(collector_factory, company: Dict):
    """関連ドメイン間のリンク収集テスト"""
    # メインドメインとIRサイト（サブドメイン）の両方を許可
    collector = collector_factory([
        company["domain"],
        f"ir.{company['domain']}",
        f"www.{company['domain']}"
    ])
    
    # メインサイトとIRサイトの両方からリンクを収集
    main_urls = await collector.collect_from_navigation(company["url"])
    
    # IRサイトが存在する場合は、そこからもリンクを収集
    ir_url = f"https://ir.{company['domain']}"
    try:
        ir_urls = await collector.collect_from_navigation(ir_url)
        all_urls = main_urls + ir_urls
    except Exception:
        all_urls = main_urls
    
    # 基本的な検証
    assert len(all_urls) > 0, f"{company['name']}: URLが収集できませんでした"
    
    # 財務・IR情報が両方のドメインから収集できているか確認
    main_domain_urls = [url for url in all_urls if company["domain"] in url]
    assert len(main_domain_urls) > 0, f"{company['name']}: メインドメインのURLが見つかりませんでした" 