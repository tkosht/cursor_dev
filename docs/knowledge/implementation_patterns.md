# 実装パターン集

## エラーハンドリングパターン

### 1. エラー階層の設計パターン

#### 1.1 基本構造
```python
class BaseCrawlerError(Exception):
    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)

class URLCollectionError(BaseCrawlerError):
    def __init__(self, message: str, url: str, status_code: Optional[int] = None):
        super().__init__(message, url=url, status_code=status_code)
```

#### 1.2 エラー変換パターン
```python
async def fetch_url(self, url: str) -> str:
    try:
        async with self.session.get(url) as response:
            if not response.ok:
                raise URLCollectionError(
                    f"Failed to fetch URL: {url}",
                    url=url,
                    status_code=response.status_code
                )
            return await response.text()
    except aiohttp.ClientError as e:
        raise URLCollectionError(f"Network error: {str(e)}", url=url)
    except asyncio.TimeoutError:
        raise URLCollectionError(f"Timeout while fetching: {url}", url=url)
```

### 2. ログ出力パターン

#### 2.1 構造化ログ
```python
def log_error(logger: Logger, error: BaseCrawlerError):
    extra = {
        "error_type": error.__class__.__name__,
        "error_message": str(error)
    }
    for key, value in error.__dict__.items():
        if key != "message":
            extra[key] = value
    
    logger.error(
        f"{error.__class__.__name__} occurred",
        extra=extra
    )
```

#### 2.2 コンテキスト付きログ
```python
@contextmanager
def log_context(logger: Logger, **context):
    try:
        yield
    except BaseCrawlerError as e:
        logger.error(
            f"Operation failed: {str(e)}",
            extra={**context, "error": e.__class__.__name__}
        )
        raise
```

### 3. テストパターン

#### 3.1 実URL使用パターン
```python
@pytest.mark.asyncio
async def test_url_collection():
    collector = URLCollector()
    urls = ["https://example.com", "https://test.example.com"]
    
    async with collector:
        results = await collector.collect_urls(urls)
        
    assert all(isinstance(r, str) for r in results)
    assert len(results) == len(urls)
```

#### 3.2 エラーケーステスト
```python
@pytest.mark.asyncio
async def test_error_handling():
    collector = URLCollector()
    invalid_urls = [
        "invalid://url",
        "http://nonexistent.example.com",
        "https://timeout.example.com"
    ]
    
    for url in invalid_urls:
        with pytest.raises(URLCollectionError) as exc_info:
            async with collector:
                await collector.collect_urls([url])
        
        error = exc_info.value
        assert error.url == url
        assert isinstance(str(error), str)
```

### 4. リソース管理パターン

#### 4.1 非同期コンテキストマネージャ
```python
class URLCollector:
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
```

#### 4.2 リトライ処理
```python
async def with_retry(func: Callable, max_retries: int = 3, delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except URLCollectionError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay * (2 ** attempt))
```

# テストコードの実装パターン

## 1. 外部接続を含むテストの実装パターン

```python
@pytest.mark.asyncio
async def test_external_api():
    """外部APIとの連携テスト"""
    # 実際のURLとパラメータを使用
    url = "https://www.release.tdnet.info/inbs/I_list_001_[企業コード].html"
    
    try:
        result = await api.fetch_data(url)
        
        # ビジネスルールに基づく検証
        assert "適時開示情報" in result.title
        assert len(result.content) >= 100
        assert re.match(r"\d{4}-\d{2}-\d{2}", result.date)
        
    except Exception as e:
        logger.error(f"外部API呼び出しエラー: {url}, {str(e)}")
        raise
```

## 2. ドメイン検証の実装パターン

```python
@pytest.mark.asyncio
async def test_domain_validation():
    """ドメイン検証機能のテスト"""
    # 実在する信頼できるドメイン
    trusted_domains = [
        "jpx.co.jp",         # 取引所
        "release.tdnet.info" # 適時開示
    ]
    
    for domain in trusted_domains:
        is_trusted = await validator.validate_domain(domain)
        assert is_trusted, f"信頼できるドメインの検証に失敗: {domain}"
```

## 3. データ抽出の実装パターン

```python
@pytest.mark.asyncio
async def test_data_extraction():
    """データ抽出機能のテスト"""
    # 実際のIR情報フォーマット
    test_data = {
        "title": "2024年3月期 第3四半期決算短信",
        "date": "2024-01-25",
        "content": "当社の2024年3月期第3四半期の連結業績についてお知らせいたします。"
    }
    
    extracted = await extractor.extract(test_data)
    
    # ビジネスルールに基づく検証
    assert len(extracted.title) >= 3
    assert len(extracted.title) <= 200
    assert len(extracted.content) >= 50
    assert len(extracted.date) == 10  # YYYY-MM-DD
```

## 4. エラーハンドリングの実装パターン

```python
@pytest.mark.asyncio
async def test_error_handling():
    """エラーハンドリング機能のテスト"""
    # 実際のエラーケース
    invalid_urls = [
        "https://suspicious-financial.com",  # 信頼性の低いドメイン
        "https://unofficial-stock-info.net"  # 非公式サイト
    ]
    
    for url in invalid_urls:
        with pytest.raises(NoValidDataError) as exc:
            await crawler.fetch(url)
        assert "信頼性の低いドメイン" in str(exc.value)
```

## 5. 同時リクエストの実装パターン

```python
@pytest.mark.asyncio
async def test_concurrent_requests():
    """同時リクエスト制限のテスト"""
    urls = [
        "https://www.jpx.co.jp",
        "https://www.release.tdnet.info"
    ]
    
    tasks = [crawler.fetch(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 結果の検証
    success_count = len([r for r in results if not isinstance(r, Exception)])
    assert success_count > 0, "すべてのリクエストが失敗"
```

## 6. データ信頼性評価の実装パターン

```python
@pytest.mark.asyncio
async def test_data_reliability():
    """データ信頼性評価機能のテスト"""
    test_cases = [
        {
            "url": "https://www.jpx.co.jp",
            "min_score": 0.8  # 取引所は高信頼性
        },
        {
            "url": "https://unofficial-site.com",
            "max_score": 0.3  # 非公式サイトは低信頼性
        }
    ]
    
    for case in test_cases:
        score = await evaluator.evaluate_reliability(case["url"])
        if "min_score" in case:
            assert score >= case["min_score"]
        if "max_score" in case:
            assert score <= case["max_score"]
```

これらのパターンは、`knowledge.md`に記載された原則に基づいて実装されています。
各パターンは、実際のビジネスケースを想定し、具体的なドメインやデータを使用しています。 