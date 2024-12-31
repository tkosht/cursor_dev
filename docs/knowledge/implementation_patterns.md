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

# 外部サービス連携テストのパターン

## 実装パターン1: 実際のサービスを使用したテスト
```python
@pytest_asyncio.fixture
async def llm_manager():
    api_key = os.getenv("API_KEY")
    if not api_key:
        pytest.skip("API_KEY not set")
    
    manager = LLMManager()
    await manager.load_model("model-name", api_key)
    return manager

@pytest.mark.asyncio
async def test_service_integration(llm_manager):
    """実際のサービスを使用した統合テスト"""
    result = await llm_manager.process_data(test_data)
    assert result is not None
    assert "expected_field" in result
```

### 利点
- 実際の動作を正確に検証可能
- エラーケースや遅延を実環境で確認可能
- 本番環境での問題を早期発見可能

### 使用場面
- 外部APIとの統合テスト
- エンドツーエンドテスト
- パフォーマンステスト

## 実装パターン2: 必要最小限のモック（例外的なケース）
```python
@pytest.fixture
def mock_service(monkeypatch):
    """内部ロジックテスト用の最小限のモック"""
    async def mock_api_call(*args, **kwargs):
        return {"status": "success"}
    
    monkeypatch.setattr(
        "package.service.api_call",
        mock_api_call
    )

@pytest.mark.asyncio
async def test_internal_logic(mock_service):
    """内部ロジックの単体テスト"""
    result = await process_internal_data()
    assert result.status == "success"
```

### 使用条件
- ユーザーからの明示的な許可がある
- 内部ロジックの単体テストに限定
- 外部サービスが完全に利用不可能

### 注意点
- モックは必要最小限に留める
- 実際の動作を可能な限り正確に再現
- テストの目的を明確に文書化

## 1. 適応的検索パターン

### 1.1 基本構造
```python
class AdaptiveCrawler:
    def __init__(self, config: Dict[str, Any]):
        self._llm_manager = LLMManager()
        self._search_manager = SearchManager()
        self._extraction_manager = ExtractionManager()
        self._config = config
        self._llm_initialized = False
        self._retry_count = 0
        self._last_error = None

    async def crawl_ir_info(
        self,
        company_code: str,
        required_fields: List[str]
    ) -> Dict[str, Any]:
        try:
            if not self._llm_initialized:
                await self.initialize_llm()

            while self._retry_count < self._config["max_attempts"]:
                try:
                    keywords = await self._generate_search_keywords(
                        company_code,
                        required_fields
                    )
                    urls = await self._search_urls(keywords)
                    data = await self._extract_data(urls, required_fields)
                    if self._validate_data(data, required_fields):
                        return data
                except Exception as e:
                    self._last_error = e
                    await self._handle_error()
                    self._retry_count += 1

            raise MaxRetriesExceededError()

        except Exception as e:
            logger.error(f"Crawling failed: {str(e)}")
            raise

### 1.2 検索キーワード生成
```python
async def _generate_search_keywords(
    self,
    company_code: str,
    required_fields: List[str]
) -> List[str]:
    context = {
        "company_code": company_code,
        "fields": required_fields,
        "attempt": self._retry_count
    }
    return await self._llm_manager.generate_keywords(context)
```

### 1.3 URL検索
```python
async def _search_urls(self, keywords: List[str]) -> List[str]:
    options = {
        "num": 10,
        "site_restrict": self._config.get("site_restrict"),
        "date_restrict": self._config.get("date_restrict")
    }
    results = await self._search_manager.search(keywords, options)
    return [r.url for r in results if r.score >= THRESHOLDS["relevance"]]
```

### 1.4 データ抽出
```python
async def _extract_data(
    self,
    urls: List[str],
    required_fields: List[str]
) -> Dict[str, Any]:
    for url in urls:
        try:
            data = await self._extraction_manager.extract(url, required_fields)
            if data.validation_score >= THRESHOLDS["validation"]:
                return data.data
        except ExtractionError as e:
            logger.warning(f"Extraction failed for {url}: {str(e)}")
            continue
    raise NoValidDataError()
```

### 1.5 エラーハンドリング
```python
async def _handle_error(self) -> None:
    delay = min(
        self._config["base_delay"] * (2 ** self._retry_count),
        self._config["max_delay"]
    )
    logger.warning(
        f"Retry {self._retry_count + 1} after {delay}s due to {self._last_error}"
    )
    await asyncio.sleep(delay)
```

## 2. LLM管理パターン

### 2.1 プロンプトテンプレート
```python
class LLMManager:
    def _load_prompt_templates(self) -> Dict[str, str]:
        return {
            "keyword_generation": """
                企業コード: {company_code}
                必要な情報: {fields}
                試行回数: {attempt}
                
                上記の情報を取得するための効果的な検索キーワードを
                5つ生成してください。
            """,
            "data_validation": """
                取得データ: {data}
                期待データ: {expected}
                
                取得データが期待データの要件を満たしているか
                検証してください。
            """
        }
```

### 2.2 キーワード生成
```python
async def generate_keywords(
    self,
    context: Dict[str, Any]
) -> List[str]:
    prompt = self._prompt_templates["keyword_generation"].format(**context)
    response = await self._llm.generate(prompt)
    return self._parse_keywords(response)
```

## 3. 検索管理パターン

### 3.1 検索実行
```python
class SearchManager:
    async def search(
        self,
        keywords: List[str],
        options: Dict[str, Any]
    ) -> List[SearchResult]:
        query = " OR ".join(keywords)
        try:
            results = await self._execute_search(query, options)
            return [
                SearchResult(
                    url=item["link"],
                    title=item["title"],
                    snippet=item["snippet"],
                    score=self._calculate_relevance(item, keywords)
                )
                for item in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise SearchError(str(e))
```

### 3.2 関連性計算
```python
def _calculate_relevance(
    self,
    item: Dict[str, Any],
    keywords: List[str]
) -> float:
    text = f"{item['title']} {item['snippet']}"
    return sum(
        text.lower().count(k.lower()) for k in keywords
    ) / len(keywords)
```

## 4. データ抽出パターン

### 4.1 ページ取得
```python
class ExtractionManager:
    async def _fetch_page(self, url: str) -> str:
        async with self._session.get(url) as response:
            if response.status != 200:
                raise ExtractionError(f"HTTP {response.status}")
            return await response.text()
```

### 4.2 検証スコア計算
```python
def _calculate_validation_score(
    self,
    data: Dict[str, Any],
    target_data: List[str]
) -> float:
    return len([k for k in target_data if k in data]) / len(target_data)
```

## 5. 設定パターン

### 5.1 タイムアウト設定
```python
TIMEOUTS = {
    "llm": 30,        # 秒
    "search": 10,     # 秒
    "extraction": 45, # 秒
    "total": 90       # 秒
}
```

### 5.2 再試行設定
```python
RETRY_CONFIG = {
    "max_attempts": 5,
    "base_delay": 2,  # 秒
    "max_delay": 32   # 秒
}
```

### 5.3 検証閾値
```python
THRESHOLDS = {
    "relevance": 0.7,
    "validation": 0.8,
    "confidence": 0.6
}
``` 