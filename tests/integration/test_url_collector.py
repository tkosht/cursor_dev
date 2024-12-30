"""
URLCollectorの統合テスト
"""

import asyncio

import pytest
from aiohttp import web

from app.crawlers.url_collector import URLCollector
from app.errors.url_analysis_errors import NetworkError, RateLimitError


@pytest.fixture
def url_collector():
    return URLCollector(
        max_concurrent_requests=2,
        request_timeout=5.0
    )


@pytest.fixture
async def test_app():
    """テスト用のアプリケーション"""
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

    async def handle_rate_limit(request):
        return web.Response(status=429)

    async def handle_error(request):
        return web.Response(status=503)

    async def handle_timeout(request):
        await asyncio.sleep(1)
        return web.Response(text="timeout")

    app = web.Application()
    app.router.add_get('/', handle_navigation)
    app.router.add_get('/robots.txt', handle_robots)
    app.router.add_get('/sitemap1.xml', handle_sitemap)
    app.router.add_get('/sitemap2.xml', handle_sitemap)
    app.router.add_get('/rate-limit', handle_rate_limit)
    app.router.add_get('/error', handle_error)
    app.router.add_get('/timeout', handle_timeout)

    return app


@pytest.fixture
async def test_client(aiohttp_client, test_app):
    """テスト用のクライアント"""
    return await aiohttp_client(await test_app)


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