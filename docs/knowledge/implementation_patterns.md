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
      "Accept-Encoding": "gzip, deflate",  # brを除外
      "Connection": "keep-alive",
      "Upgrade-Insecure-Requests": "1",
      "Cache-Control": "no-cache",
      "DNT": "1",
      "Sec-GPC": "1",
      "Pragma": "no-cache",
      "Referer": "https://www.google.com/"
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
      async def analyze_site_structure(self, url: str) -> Dict[str, Any]:
          """サイト構造を動的に解析"""
          content = await self._fetch_page(url)
          return await self._analyze_content(content)
          
      async def find_target_page(self, base_url: str, target_type: str) -> str:
          """目的のページを動的に探索"""
          structure = await self.analyze_site_structure(base_url)
          return await self._identify_page(structure, target_type)
          
      async def extract_data(self, page_url: str, target_data: Dict[str, str]) -> Dict[str, str]:
          """データを抽出"""
          content = await self._fetch_page(page_url)
          return await self._extract_target_data(content, target_data)
  ```

### 適応的クローリングのテストパターン
- **目的**: 動的な探索・抽出機能の検証
- **実装ポイント**:
  ```python
  class AdaptiveCrawlerTest:
      @pytest.mark.asyncio
      async def test_site_structure_analysis(self):
          """サイト構造の解析機能をテスト"""
          crawler = AdaptiveCrawler()
          structure = await crawler.analyze_site_structure("https://example.com")
          assert "navigation" in structure
          assert "main_content" in structure
          
      @pytest.mark.asyncio
      async def test_target_page_discovery(self):
          """目的のページの動的探索をテスト"""
          crawler = AdaptiveCrawler()
          ir_page = await crawler.find_target_page(
              "https://example.com",
              target_type="ir_info"
          )
          assert ir_page.endswith("/ir") or "investor" in ir_page
          
      @pytest.mark.asyncio
      async def test_data_extraction(self):
          """データ抽出機能をテスト"""
          crawler = AdaptiveCrawler()
          data = await crawler.extract_data(
              "https://example.com/ir",
              {"revenue": "売上高"}
          )
          assert "revenue" in data
          assert "円" in data["revenue"]
  ```

### 統合テストパターン
- **目的**: 実サイトを使用した信頼性の高いテスト
- **実装ポイント**:
  ```python
  class IRSiteIntegrationTest:
      @pytest.mark.asyncio
      async def test_ir_page_access(self):
          crawler = AdaptiveCrawler(
              retry_delay=5.0,  # 5秒待機
              max_concurrent=1,  # 同時接続数制限
              timeout_total=90,
              timeout_connect=30,
              timeout_read=45
          )
          async with crawler as client:
              result = await client.crawl("https://example.com")
              assert result is not None
              await asyncio.sleep(5)  # レート制限対策
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
              
      @pytest.mark.asyncio
      async def test_rate_limit_handling(self):
          for _ in range(3):
              await crawler.crawl(url)
              await asyncio.sleep(5)  # レート制限対策
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
      def __init__(self, max_concurrent: int = 1):
          self._semaphore = asyncio.Semaphore(max_concurrent)
          
      async def execute(self, coro):
          async with self._semaphore:
              result = await coro
              await asyncio.sleep(5)  # レート制限対策
              return result
  ```

### LLMOptimization パターン
- **目的**: LLMを活用したクローリング最適化
- **実装ポイント**:
  ```python
  class LLMOptimizer:
      async def optimize_selector(self, html: str, target: str) -> str:
          context = self._analyze_html_structure(html)
          return await self._generate_optimal_selector(context, target)
          
      async def _generate_optimal_selector(
          self,
          context: str,
          target: str,
          timeout: int = 30
      ) -> str:
          """タイムアウト付きでLLMを使用"""
          try:
              async with asyncio.timeout(timeout):
                  return await self.llm.generate(
                      f"コンテキスト: {context}\n"
                      f"ターゲット: {target}"
                  )
          except asyncio.TimeoutError:
              logger.error("LLM通信タイムアウト")
              raise
  ``` 

# キャッシュ制御パターン

## HTTPキャッシュ制御
プロジェクト全体で統一されたキャッシュ制御設定を使用します：

```python
CACHE_CONTROL_HEADERS = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}
```

### 設定の理由
1. `no-cache`: 
   - 毎回サーバーに再検証を要求
   - キャッシュは許可するが、使用前に必ず新鮮度の確認が必要
   - 条件付きリクエストによる帯域幅の節約が可能

2. `Pragma: no-cache`:
   - HTTP/1.0との後方互換性のため
   - 古いプロキシサーバーでも確実にキャッシュを防止

### 使用方法
1. クローラーやサイトアナライザーでのHTTPリクエスト時に設定
2. 常に最新のコンテンツを取得する必要がある場合に使用
3. ヘッダーは基本設定として組み込み、必要に応じてオーバーライド可能

### 注意点
- `max-age=0`ではなく`no-cache`を使用
- キャッシュの完全な無効化が必要な場合は`no-store`を検討
- プロキシサーバー経由のアクセスも考慮した設定

### 実装例
```python
def create_headers():
    return {
        "User-Agent": "Mozilla/5.0...",
        "Accept": "text/html,application/xhtml+xml...",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        # その他のヘッダー
    }
``` 

# テストパターン集

## 非同期テストパターン
- **目的**: 非同期処理を含むテストの安定性確保
- **実装ポイント**:
  ```python
  @pytest.mark.asyncio
  async def test_async_operation():
      # タイムアウト設定
      async with asyncio.timeout(30):
          # テスト実行
          result = await async_operation()
          assert result is not None

  @pytest.mark.asyncio
  async def test_with_retry():
      # リトライ付きテスト
      for attempt in range(3):
          try:
              result = await async_operation()
              assert result is not None
              break
          except Exception as e:
              if attempt == 2:
                  raise
              await asyncio.sleep(1)
  ```

## カバレッジ最適化パターン
- **目的**: テストカバレッジの効率的な向上
- **実装ポイント**:
  ```python
  class TestWithCoverage:
      @pytest.mark.parametrize("input,expected", [
          ("normal", True),
          ("edge_case", False),
          ("error_case", None)
      ])
      def test_multiple_cases(self, input, expected):
          """パラメータ化テストでカバレッジ向上"""
          result = target_function(input)
          assert result == expected

      def test_error_handling(self):
          """エラーケースのカバレッジ"""
          with pytest.raises(ValueError):
              target_function("invalid")
  ```

## モデル依存関係テストパターン
- **目的**: SQLAlchemyモデル間の依存関係の検証
- **実装ポイント**:
  ```python
  class TestModelRelations:
      def test_model_initialization(self):
          """モデルの初期化順序テスト"""
          parent = ParentModel()
          child = ChildModel(parent=parent)
          assert child.parent_id == parent.id

      def test_cascade_operations(self):
          """カスケード操作のテスト"""
          parent = ParentModel()
          child = ChildModel(parent=parent)
          session.add(parent)
          session.commit()
          session.delete(parent)
          session.commit()
          assert session.query(ChildModel).count() == 0
  ```

## キャッシュ制御テストパターン
- **目的**: HTTPキャッシュ制御の検証
- **実装ポイント**:
  ```python
  class TestCacheControl:
      async def test_cache_headers(self):
          """キャッシュヘッダーの検証"""
          client = HTTPClient()
          headers = client.headers
          assert headers["Cache-Control"] == "no-cache"
          assert headers["Pragma"] == "no-cache"

      async def test_cache_behavior(self):
          """キャッシュ動作の検証"""
          client = HTTPClient()
          response1 = await client.get(url)
          response2 = await client.get(url)
          assert response1.headers != response2.headers
  ``` 