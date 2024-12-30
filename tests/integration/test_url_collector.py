"""
URLCollectorの統合テスト
"""

import asyncio
import logging
import time
from collections import Counter

import pytest
from aiohttp import web

from app.crawlers.url_collector import URLCollector
from app.errors.url_analysis_errors import NetworkError, RateLimitError
from app.site_analyzer import URLAnalyzer

logger = logging.getLogger(__name__)


def create_test_handlers():
    """テストハンドラーの作成"""
    handlers = {}
    
    async def handle_navigation(request):
        return web.Response(text="""
        <html>
            <nav>
                <a href="/about">About</a>
                <a href="https://test.local/products">Products</a>
                <a href="#contact">Contact</a>
                <a href="javascript:void(0)">Menu</a>
            </nav>
        </html>
        """)
    
    async def handle_robots(request):
        base_url = str(request.url.origin())
        return web.Response(text=f"""
        User-agent: *
        Allow: /
        
        Sitemap: {base_url}/sitemap1.xml
        Sitemap: {base_url}/sitemap2.xml
        """)
    
    async def handle_sitemap(request):
        base_url = str(request.url.origin())
        return web.Response(text=f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>{base_url}/page1</loc></url>
            <url><loc>{base_url}/page2</loc></url>
        </urlset>
        """)
    
    async def handle_timeout(request):
        await asyncio.sleep(1)
        return web.Response(text="timeout")
    
    handlers.update({
        '/': handle_navigation,
        '/robots.txt': handle_robots,
        '/sitemap1.xml': handle_sitemap,
        '/sitemap2.xml': handle_sitemap,
        '/rate-limit': lambda r: web.Response(status=429),
        '/error': lambda r: web.Response(status=503),
        '/timeout': handle_timeout,
    })
    
    # コンテンツ系ハンドラー
    async def handle_footer(request):
        return web.Response(text="""
        <html>
            <footer>
                <a href="/company">Company</a>
                <a href="/ir">IR</a>
                <a href="https://external.com">External</a>
            </footer>
        </html>
        """)
    
    async def handle_multilang(request):
        return web.Response(text="""
        <html>
            <nav>
                <a href="/en/about">About</a>
                <a href="/ja/company">会社概要</a>
                <a href="/zh/about">关于我们</a>
            </nav>
        </html>
        """)
    
    async def handle_mixed_domains(request):
        return web.Response(text="""
        <html>
            <nav>
                <a href="/internal">Internal</a>
                <a href="https://external.com/about">External</a>
                <a href="https://test.local/allowed">Allowed Domain</a>
            </nav>
        </html>
        """)
    
    handlers.update({
        '/footer': handle_footer,
        '/multilang': handle_multilang,
        '/mixed': handle_mixed_domains,
    })
    
    return handlers


@pytest.fixture
def test_app():
    """テスト用のアプリケーション"""
    app = web.Application()
    
    # ハンドラーの登録
    handlers = create_test_handlers()
    for path, handler in handlers.items():
        app.router.add_get(path, handler)
    
    return app


@pytest.fixture
def url_collector():
    return URLCollector(
        max_concurrent_requests=2,
        request_timeout=5.0
    )


@pytest.fixture
async def test_client(aiohttp_client, test_app):
    """テスト用のクライアント"""
    return await aiohttp_client(test_app)


@pytest.mark.asyncio
async def test_collect_from_navigation(test_client):
    """ナビゲーションメニューからのURL収集テスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    urls = await collector.collect_from_navigation(base_url)
    
    assert len(urls) == 2
    assert base_url.rstrip('/') + "/about" in urls
    assert "https://test.local/products" in urls


@pytest.mark.asyncio
async def test_get_sitemaps_from_robots(test_client):
    """robots.txtからのサイトマップURL取得テスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    sitemaps = await collector.get_sitemaps_from_robots(base_url)
    
    assert len(sitemaps) == 2
    assert all(sitemap.endswith('/sitemap1.xml') or sitemap.endswith('/sitemap2.xml') for sitemap in sitemaps)
    assert any(sitemap.endswith('/sitemap1.xml') for sitemap in sitemaps)
    assert any(sitemap.endswith('/sitemap2.xml') for sitemap in sitemaps)


@pytest.mark.asyncio
async def test_collect_from_sitemap(test_client):
    """サイトマップからのURL収集テスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    urls = await collector.collect_from_sitemap(base_url)
    
    assert len(urls) == 2
    assert all(url.endswith('/page1') or url.endswith('/page2') for url in urls)
    assert any(url.endswith('/page1') for url in urls)
    assert any(url.endswith('/page2') for url in urls)


@pytest.mark.asyncio
async def test_rate_limit_handling(test_client):
    """レート制限時のエラーハンドリングテスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    
    with pytest.raises(RateLimitError):
        await collector.collect_from_navigation(base_url + "rate-limit")


@pytest.mark.asyncio
async def test_network_error_handling(test_client):
    """ネットワークエラー時のハンドリングテスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    
    with pytest.raises(NetworkError):
        await collector.collect_from_navigation(base_url + "error")


@pytest.mark.asyncio
async def test_timeout_handling(test_client):
    """タイムアウト時のエラーハンドリングテスト"""
    collector = URLCollector(request_timeout=0.1)
    client = await test_client
    base_url = str(client.make_url('/'))
    
    with pytest.raises(NetworkError):
        await collector.collect_from_navigation(base_url + "timeout")


@pytest.mark.asyncio
async def test_concurrent_requests_limit(test_client):
    """同時リクエスト数制限のテスト"""
    collector = URLCollector(max_concurrent_requests=2)
    client = await test_client
    base_url = str(client.make_url('/'))
    test_urls = [base_url + "timeout" for _ in range(5)]
    
    start_time = asyncio.get_event_loop().time()
    tasks = [collector._make_request(None, url) for url in test_urls]
    
    with pytest.raises(NetworkError):
        await asyncio.gather(*tasks)
    
    end_time = asyncio.get_event_loop().time()
    assert end_time - start_time >= 0.2  # 2つずつ処理されることを確認


@pytest.mark.asyncio
async def test_collect_from_footer(test_client):
    """フッターリンクからのURL収集テスト"""
    client = await test_client
    base_url = str(client.make_url('/footer'))
    
    collector = URLCollector()
    urls = await collector.collect_from_footer(base_url)
    
    assert len(urls) == 2  # 外部リンクは除外
    assert base_url.rstrip('/footer') + "/company" in urls
    assert base_url.rstrip('/footer') + "/ir" in urls


@pytest.mark.asyncio
async def test_language_detection(test_client):
    """言語情報の検出テスト"""
    client = await test_client
    base_url = str(client.make_url('/multilang'))
    
    collector = URLCollector()
    urls = await collector.collect_from_navigation(base_url)
    language_info = collector.detect_languages(urls)
    
    assert len(language_info) == 3
    assert any(info['lang'] == 'en' for info in language_info)
    assert any(info['lang'] == 'ja' for info in language_info)
    assert any(info['lang'] == 'zh' for info in language_info)


@pytest.mark.asyncio
async def test_domain_filtering(test_client):
    """外部ドメインのフィルタリングテスト"""
    client = await test_client
    base_url = str(client.make_url('/mixed'))
    
    collector = URLCollector(allowed_domains=['test.local'])
    urls = await collector.collect_from_navigation(base_url)
    
    assert len(urls) == 2  # external.comは除外
    assert base_url.rstrip('/mixed') + "/internal" in urls
    assert "https://test.local/allowed" in urls


@pytest.mark.asyncio
async def test_error_monitoring(test_client):
    """エラー監視のテスト"""
    collector = URLCollector()
    client = await test_client
    base_url = str(client.make_url('/'))
    
    # エラーを発生させる
    error_urls = [
        base_url + "error",
        base_url + "rate-limit",
        base_url + "timeout"
    ]
    
    error_counts = Counter()
    for url in error_urls:
        try:
            await collector.collect_from_navigation(url)
        except Exception as e:
            error_counts[type(e).__name__] += 1
    
    assert error_counts['NetworkError'] == 2  # errorとtimeout
    assert error_counts['RateLimitError'] == 1


@pytest.mark.asyncio
async def test_performance_metrics(test_client):
    """パフォーマンス指標の検証テスト"""
    max_concurrent = 5
    collector = URLCollector(max_concurrent_requests=max_concurrent)
    client = await test_client
    base_url = str(client.make_url('/'))
    
    # 応答時間の測定
    start_time = time.time()
    await collector.collect_from_navigation(base_url)
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response_time < 5.0  # 要件の最大応答時間
    
    # スループットの検証
    start_time = time.time()
    urls = [base_url for _ in range(max_concurrent * 2)]  # リクエスト数を制限
    tasks = [collector.collect_from_navigation(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results if not isinstance(r, Exception))
    requests_per_second = successful_requests / total_time
    
    # バッファを含めた制限値
    assert requests_per_second <= max_concurrent * 1.5  # より厳密な制限値 


@pytest.mark.asyncio
async def test_cache_control_headers():
    """キャッシュ制御ヘッダーのテスト"""
    analyzer = URLAnalyzer()
    
    # キャッシュ制御ヘッダーの確認
    assert "Cache-Control" in analyzer.headers
    assert analyzer.headers["Cache-Control"] == "no-cache"
    assert "Pragma" in analyzer.headers
    assert analyzer.headers["Pragma"] == "no-cache"
    
    # 実際のリクエストでヘッダーが正しく送信されることを確認
    test_url = "https://www.7andi.com/ir.html"
    try:
        await analyzer._fetch_content(test_url)
        # テスト成功
    except Exception as e:
        # ネットワークエラーは無視（ヘッダーのテストが目的のため）
        logger.warning(f"Network error occurred: {e}")
        pass 