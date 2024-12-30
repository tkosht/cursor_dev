# AdaptiveCrawler詳細設計

## 1. アクセス制御の詳細設計

### 1.1 アクセス間隔制御
```python
class AccessController:
    def __init__(self):
        # 同一URLへの最終アクセス時刻を記録
        self.last_access_times: Dict[str, datetime] = {}
        # 同時接続数を制御するセマフォ
        self.semaphore = asyncio.Semaphore(5)
        # アクセス間隔（秒）
        self.min_interval = 3600
        
    async def check_access(self, url: str) -> None:
        """アクセス制御チェックを実行"""
        domain = self._extract_domain(url)
        await self._check_domain_access(domain)
        await self._check_url_access(url)
        await self.semaphore.acquire()
        
    def _extract_domain(self, url: str) -> str:
        """URLからドメインを抽出"""
        parsed = urlparse(url)
        return parsed.netloc
        
    async def _check_domain_access(self, domain: str) -> None:
        """ドメインごとのアクセス制御"""
        last_time = self.last_access_times.get(domain)
        if last_time and (datetime.now() - last_time).seconds < self.min_interval:
            raise TooFrequentAccessError(f"Domain access too frequent: {domain}")
            
    async def _check_url_access(self, url: str) -> None:
        """URL単位のアクセス制御"""
        last_time = self.last_access_times.get(url)
        if last_time and (datetime.now() - last_time).seconds < self.min_interval:
            raise TooFrequentAccessError(f"URL access too frequent: {url}")
```

### 1.2 エラーハンドリング
```python
class ErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0
        
    async def handle(self, error: Exception) -> Dict:
        """エラーハンドリングの実行"""
        if isinstance(error, aiohttp.ClientError):
            return await self._handle_network_error(error)
        elif isinstance(error, TooFrequentAccessError):
            return await self._handle_access_error(error)
        else:
            return await self._handle_unknown_error(error)
            
    async def _handle_network_error(self, error: aiohttp.ClientError) -> Dict:
        """ネットワークエラーの処理"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                delay = self.base_delay * (2 ** retry_count)
                await asyncio.sleep(delay)
                # リトライ処理
                return {"status": "retry", "attempt": retry_count + 1}
            except Exception as e:
                retry_count += 1
        return {"status": "error", "message": str(error)}
        
    async def _handle_access_error(self, error: TooFrequentAccessError) -> Dict:
        """アクセス制御エラーの処理"""
        return {
            "status": "error",
            "message": str(error),
            "retry_after": self.min_interval
        }
```

## 2. 外部接続の詳細設計

### 2.1 HTTPクライアント設定
```python
class AdaptiveCrawler:
    def _create_client_session(self) -> aiohttp.ClientSession:
        """HTTPクライアントセッションの作成"""
        timeout = aiohttp.ClientTimeout(
            total=60.0,
            connect=20.0,
            sock_connect=20.0,
            sock_read=20.0
        )
        
        return aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "User-Agent": "AdaptiveCrawler/1.0",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
            },
            connector=aiohttp.TCPConnector(
                limit=10,
                enable_cleanup_closed=True,
                force_close=False,
                keepalive_timeout=60.0
            )
        )
```

### 2.2 リクエスト実行
```python
class AdaptiveCrawler:
    async def _execute_request(
        self,
        session: aiohttp.ClientSession,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> aiohttp.ClientResponse:
        """HTTPリクエストの実行"""
        try:
            response = await session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except aiohttp.ClientError as e:
            raise RequestError(f"Request failed: {str(e)}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timeout: {url}")
```

## 3. ログ出力の詳細設計

### 3.1 ログフォーマット
```python
class Logger:
    def __init__(self):
        self.logger = logging.getLogger("adaptive_crawler")
        self.logger.setLevel(logging.INFO)
        
        # ファイルハンドラ
        fh = logging.FileHandler("crawler.log")
        fh.setLevel(logging.INFO)
        
        # フォーマッタ
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
```

### 3.2 メトリクス収集
```python
class Metrics:
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.retry_count = 0
        self.total_time = 0.0
        
    def record_success(self, time_taken: float):
        """成功メトリクスの記録"""
        self.success_count += 1
        self.total_time += time_taken
        
    def record_error(self):
        """エラーメトリクスの記録"""
        self.error_count += 1
        
    def record_retry(self):
        """リトライメトリクスの記録"""
        self.retry_count += 1
        
    def get_success_rate(self) -> float:
        """成功率の計算"""
        total = self.success_count + self.error_count
        return self.success_count / total if total > 0 else 0.0
        
    def get_average_time(self) -> float:
        """平均処理時間の計算"""
        return self.total_time / self.success_count if self.success_count > 0 else 0.0
``` 