# 実装パターン集

## 非同期テストの実装パターン

### 基本的なテストケース
```python
import pytest
from aiohttp import web

@pytest.mark.asyncio
async def test_basic_async():
    # テスト用のアプリケーション作成
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text='test'))
    
    # テストクライアントの取得
    async with aiohttp_client(app) as client:
        # テストの実行
        response = await client.get('/')
        assert response.status == 200
        text = await response.text()
        assert text == 'test'
```

### エラーハンドリングのテスト
```python
@pytest.mark.asyncio
async def test_error_handling():
    # エラーレスポンスを返すハンドラー
    async def error_handler(request):
        return web.Response(status=503)
    
    # テストアプリケーションの設定
    app = web.Application()
    app.router.add_get('/error', error_handler)
    
    # テストの実行
    async with aiohttp_client(app) as client:
        with pytest.raises(NetworkError):
            await client.get('/error')
```

### 同時実行制限のテスト
```python
@pytest.mark.asyncio
async def test_concurrent_limit():
    # 遅延レスポンスを返すハンドラー
    async def delay_handler(request):
        await asyncio.sleep(0.1)
        return web.Response(text='ok')
    
    # テストアプリケーションの設定
    app = web.Application()
    app.router.add_get('/delay', delay_handler)
    
    # テストの実行
    async with aiohttp_client(app) as client:
        start_time = asyncio.get_event_loop().time()
        tasks = [client.get('/delay') for _ in range(5)]
        await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        # 2つずつ処理されるため、少なくとも0.3秒かかるはず
        assert end_time - start_time >= 0.3
```

## テストサーバーの実装パターン

### 基本的なサーバー設定
```python
@pytest.fixture
async def test_app():
    """テスト用のアプリケーション"""
    async def handle_request(request):
        return web.Response(text='test')
    
    app = web.Application()
    app.router.add_get('/', handle_request)
    return app

@pytest.fixture
async def test_client(test_app, aiohttp_client):
    """テスト用のクライアント"""
    return await aiohttp_client(test_app)
```

### 複数エンドポイントの設定
```python
@pytest.fixture
async def test_app():
    """複数のエンドポイントを持つテストアプリケーション"""
    app = web.Application()
    
    # 通常のレスポンス
    app.router.add_get('/', lambda r: web.Response(text='ok'))
    
    # エラーレスポンス
    app.router.add_get('/error', lambda r: web.Response(status=503))
    
    # 遅延レスポンス
    app.router.add_get('/delay', 
        lambda r: asyncio.sleep(0.1).then(
            lambda _: web.Response(text='delayed')
        )
    )
    
    return app
```

### レスポンスの動的生成
```python
@pytest.fixture
async def test_app():
    """動的なレスポンスを返すテストアプリケーション"""
    async def dynamic_handler(request):
        query = request.query.get('type', 'default')
        if query == 'error':
            return web.Response(status=503)
        elif query == 'delay':
            await asyncio.sleep(0.1)
            return web.Response(text='delayed')
        else:
            return web.Response(text='default')
    
    app = web.Application()
    app.router.add_get('/', dynamic_handler)
    return app
```

## XMLの名前空間対応パターン
```python
def extract_with_namespace(element: ET.Element, xpath: str) -> List[str]:
    """名前空間を考慮したXML要素の抽出

    Args:
        element: XML要素
        xpath: 検索パス

    Returns:
        抽出された要素のリスト
    """
    # 複数の名前空間パターンを定義
    namespaces = {
        "default": "http://www.example.org/schema",
        "alt": "http://www.example.org/schema/alt"
    }
    
    results = []
    # 各名前空間でトライ
    for namespace in namespaces.values():
        # 名前空間を使用した検索
        found = element.findall(".//{%s}target" % namespace)
        if found:
            results.extend([item.text for item in found if item.text])
            break
    
    # 名前空間なしでもトライ（フォールバック）
    if not results:
        found = element.findall(".//target")
        results.extend([item.text for item in found if item.text])
    
    return results
```

## URL正規化パターン
```python
from urllib.parse import urljoin, urlparse

def normalize_url(url: str, base_url: str) -> str:
    """URLの正規化

    Args:
        url: 対象URL（相対パスの可能性あり）
        base_url: 基準URL

    Returns:
        正規化されたURL
    """
    # javascript:やdata:などのスキームは除外
    if url.startswith(("javascript:", "data:", "mailto:", "#")):
        return ""
    
    # 相対パスの場合は絶対URLに変換
    if not url.startswith(("http://", "https://")):
        url = urljoin(base_url, url.lstrip("/"))
    
    # URLの正規化
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized
```

## 非同期リクエスト制御パターン
```python
import asyncio
from typing import Optional

import aiohttp

class RequestController:
    """非同期リクエストの制御を行うクラス"""

    def __init__(
        self,
        max_concurrent: int = 3,
        timeout: float = 30.0,
        headers: Optional[dict] = None
    ):
        """
        Args:
            max_concurrent: 同時リクエスト数の上限
            timeout: タイムアウト時間（秒）
            headers: HTTPヘッダー
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.headers = headers or {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def request(
        self,
        session: Optional[aiohttp.ClientSession],
        url: str
    ) -> str:
        """制御された非同期リクエストの実行

        Args:
            session: セッション（Noneの場合は新規作成）
            url: リクエスト先URL

        Returns:
            レスポンス本文

        Raises:
            NetworkError: ネットワークエラー発生時
            RateLimitError: レート制限到達時
        """
        if session is None:
            session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            should_close = True
        else:
            should_close = False

        try:
            async with self._semaphore:
                try:
                    async with session.get(url) as response:
                        if response.status == 429:
                            raise RateLimitError()
                        if response.status >= 400:
                            raise NetworkError()
                        return await response.text()
                except asyncio.TimeoutError:
                    raise NetworkError()
                except aiohttp.ClientError as e:
                    raise NetworkError()
        finally:
            if should_close:
                await session.close()
```

## 非同期テストサーバーパターン
```python
import asyncio
from aiohttp import web

class TestServer:
    """非同期テスト用のサーバー"""

    def __init__(self):
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """ルーティングの設定"""
        self.app.router.add_get("/", self.handle_root)
        self.app.router.add_get("/error", self.handle_error)
        self.app.router.add_get("/timeout", self.handle_timeout)
        self.app.router.add_get("/rate-limit", self.handle_rate_limit)
    
    async def handle_root(self, request):
        """ルートパスのハンドラ"""
        return web.Response(text="OK")
    
    async def handle_error(self, request):
        """エラーパスのハンドラ"""
        return web.Response(status=503)
    
    async def handle_timeout(self, request):
        """タイムアウトパスのハンドラ"""
        await asyncio.sleep(1)
        return web.Response(text="timeout")
    
    async def handle_rate_limit(self, request):
        """レート制限パスのハンドラ"""
        return web.Response(status=429)

@pytest.fixture
async def test_client(aiohttp_client):
    """テストクライアントのフィクスチャ"""
    server = TestServer()
    return await aiohttp_client(server.app)
``` 