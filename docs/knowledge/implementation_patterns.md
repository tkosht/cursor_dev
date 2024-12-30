# 実装パターン集

## 非同期処理パターン

### RequestControllerパターン
非同期リクエストの制御と最適化のためのパターン

```python
class RequestController:
    def __init__(self, max_concurrent_requests: int = 4):
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._request_interval = 1.0 / (max_concurrent_requests * 0.5)
        self._last_request_time = 0.0

    async def execute_request(self, url: str) -> str:
        async with self._semaphore:
            # リクエスト間隔の制御
            current_time = time.time()
            elapsed = current_time - self._last_request_time
            if elapsed < self._request_interval:
                await asyncio.sleep(self._request_interval - elapsed + 0.3)
            
            # リクエストの実行
            async with self._session.get(url) as response:
                self._last_request_time = time.time()
                return await response.text()
```

### SessionManagerパターン
HTTPセッションのライフサイクル管理パターン

```python
class SessionManager:
    def __init__(self):
        self._timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self._connector = aiohttp.TCPConnector(limit=100)
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=self._timeout,
            connector=self._connector,
            headers=self.headers
        )
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
```

### ErrorHandlerパターン
非同期処理における例外処理パターン

```python
class ErrorHandler:
    async def handle_request(self, url: str) -> str:
        try:
            async with self._session.get(url, timeout=self.timeout) as response:
                if response.status == 429:
                    raise RateLimitError("レート制限に達しました")
                elif response.status >= 400:
                    raise NetworkError(f"HTTP {response.status}", status_code=response.status)
                return await response.text()
        except asyncio.TimeoutError:
            raise NetworkError("タイムアウト", status_code=408)
        except aiohttp.ClientError as e:
            raise NetworkError(f"接続エラー: {str(e)}")
```

## ドメイン管理パターン

### DomainFilterパターン
URLのドメインフィルタリングパターン

```python
class DomainFilter:
    def __init__(self, allowed_domains: Optional[List[str]] = None):
        self.allowed_domains = allowed_domains or []

    def is_allowed_domain(self, url: str, base_url: str) -> bool:
        if not url or not base_url:
            return False
        
        domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc
        
        # 同一ドメインは常に許可
        if domain == base_domain:
            return True
            
        # 許可ドメインリストがない場合は同一ドメインのみ
        if not self.allowed_domains:
            return False
            
        # 許可ドメインとそのサブドメインをチェック
        return any(
            domain == allowed or domain.endswith(f".{allowed}")
            for allowed in self.allowed_domains
        )
```

## テストパターン

### AsyncTestServerパターン
非同期テスト用のモックサーバーパターン

```python
class AsyncTestServer:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.app = web.Application()
        self.host = host
        self.port = port
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_root)
        self.app.router.add_get("/timeout", self.handle_timeout)
        self.app.router.add_get("/error", self.handle_error)

    async def handle_root(self, request):
        return web.Response(text="test response")

    async def handle_timeout(self, request):
        await asyncio.sleep(2)
        return web.Response(text="timeout")

    async def handle_error(self, request):
        raise web.HTTPInternalServerError()

    async def __aenter__(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.runner.cleanup()
```

### AsyncTestCaseパターン
非同期テストケースの基本パターン

```python
class AsyncTestCase:
    @pytest.fixture
    async def collector(self):
        async with URLCollector(max_concurrent_requests=4) as collector:
            yield collector

    @pytest.mark.asyncio
    async def test_normal_case(self, collector):
        urls = await collector.collect_urls("http://test.local/")
        assert len(urls) > 0
        assert all(url.startswith("http") for url in urls)

    @pytest.mark.asyncio
    async def test_error_cases(self, collector):
        with pytest.raises(NetworkError):
            await collector.collect_urls("http://test.local/error")

    @pytest.mark.asyncio
    async def test_performance(self, collector):
        start_time = time.time()
        tasks = [
            collector.collect_urls(f"http://test.local/page{i}")
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # スループットの検証
        operations_per_second = len(results) / (end_time - start_time)
        assert operations_per_second <= collector.max_concurrent_requests
```

## 設定管理パターン

### ConfigurationManagerパターン
環境に応じた設定管理パターン

```python
class ConfigurationManager:
    def __init__(self, env: str = "development"):
        self.env = env
        self._load_config()

    def _load_config(self):
        self.config = {
            "development": {
                "max_concurrent": 4,
                "timeout": 30,
                "allowed_domains": ["test.local", "localhost"],
                "retry_count": 3
            },
            "production": {
                "max_concurrent": 10,
                "timeout": 60,
                "allowed_domains": ["example.com", "api.example.com"],
                "retry_count": 5
            }
        }[self.env]

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    @property
    def max_concurrent(self) -> int:
        return self.get("max_concurrent", 4)

    @property
    def timeout(self) -> int:
        return self.get("timeout", 30)
``` 