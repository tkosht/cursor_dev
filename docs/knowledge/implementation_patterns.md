# 実装パターン集

## IRサイト関連パターン

### IRSiteLocator パターン
- **目的**: IRサイトのURLを動的に特定し、適切なページを選択する
- **実装ポイント**:
  ```python
  class IRSiteLocator:
      def __init__(self, base_url: str):
          self.base_url = base_url
          
      async def find_ir_page(self) -> str:
          # IRページの候補を探索
          candidates = await self._find_ir_candidates()
          # 最適なページを選択
          return await self._select_best_candidate(candidates)
  ```

### HTTP通信パターン
- **目的**: ブラウザライクな振る舞いを実現する
- **実装ポイント**:
  ```python
  BROWSER_HEADERS = {
      "User-Agent": "Mozilla/5.0 ... Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,...",
      "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
      "Accept-Encoding": "gzip, deflate, br",
      "Connection": "keep-alive",
      "Upgrade-Insecure-Requests": "1"
  }
  ```

### エラーハンドリング階層 パターン
- **目的**: 階層的なエラー処理を実現
- **実装ポイント**:
  ```python
  class HTTPError(Exception): pass
  class ParseError(Exception): pass
  class DataExtractionError(Exception): pass
  
  async def handle_error(self, error: Exception):
      if isinstance(error, HTTPError):
          return await self._handle_http_error(error)
      elif isinstance(error, ParseError):
          return await self._handle_parse_error(error)
      elif isinstance(error, DataExtractionError):
          return await self._handle_extraction_error(error)
  ```

### AdaptiveCrawler パターン
- **目的**: サイト構造の変更に適応するクローラー
- **実装ポイント**:
  ```python
  class AdaptiveCrawler:
      def __init__(self):
          self.locator = IRSiteLocator()
          self.retry_strategy = ExponentialBackoff()
          
      async def crawl(self, url: str):
          try:
              return await self._do_crawl(url)
          except Exception as e:
              return await self.retry_strategy.retry(self._do_crawl, url)
  ```

### 統合テストパターン
- **目的**: 実サイトを使用した信頼性の高いテスト
- **実装ポイント**:
  ```python
  class IRSiteIntegrationTest:
      @pytest.mark.asyncio
      async def test_ir_page_access(self):
          crawler = AdaptiveCrawler()
          result = await crawler.crawl("https://example.com")
          assert result.status == 200
  ```

### エラーケーステスト パターン
- **目的**: エラー状況の網羅的なテスト
- **実装ポイント**:
  ```python
  class ErrorCaseTest:
      @pytest.mark.asyncio
      async def test_http_error_handling(self):
          with pytest.raises(HTTPError):
              await crawler.crawl("https://non-existent.example.com")
  ```

### URL探索戦略 パターン
- **目的**: 動的なURL探索と検証
- **実装ポイント**:
  ```python
  class URLExplorer:
      async def explore(self, base_url: str) -> List[str]:
          candidates = await self._find_links(base_url)
          return [url for url in candidates if self._is_ir_page(url)]
  ```

### ConcurrencyControl パターン
- **目的**: 並行アクセスの制御
- **実装ポイント**:
  ```python
  class ConcurrencyController:
      def __init__(self, max_concurrent: int = 3):
          self._semaphore = asyncio.Semaphore(max_concurrent)
          
      async def execute(self, coro):
          async with self._semaphore:
              return await coro
  ```

### LLMOptimization パターン
- **目的**: LLMを活用したクローリング最適化
- **実装ポイント**:
  ```python
  class LLMOptimizer:
      async def optimize_selector(self, html: str, target: str) -> str:
          context = self._analyze_html_structure(html)
          return await self._generate_optimal_selector(context, target)
  ``` 