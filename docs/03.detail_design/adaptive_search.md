# 適応的検索機能詳細設計

## 1. クラス詳細設計

### 1.1 AdaptiveCrawler
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

    async def initialize_llm(self) -> None:
        """LLMの初期化を行う"""
        await self._llm_manager.initialize()
        self._llm_initialized = True

    async def crawl_ir_info(
        self,
        company_code: str,
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """IR情報のクローリングを実行"""
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

    async def _generate_search_keywords(
        self,
        company_code: str,
        required_fields: List[str]
    ) -> List[str]:
        """検索キーワードの生成"""
        context = {
            "company_code": company_code,
            "fields": required_fields,
            "attempt": self._retry_count
        }
        return await self._llm_manager.generate_keywords(context)

    async def _search_urls(self, keywords: List[str]) -> List[str]:
        """URLの検索"""
        options = {
            "num": 10,
            "site_restrict": self._config.get("site_restrict"),
            "date_restrict": self._config.get("date_restrict")
        }
        results = await self._search_manager.search(keywords, options)
        return [r.url for r in results if r.score >= THRESHOLDS["relevance"]]

    async def _extract_data(
        self,
        urls: List[str],
        required_fields: List[str]
    ) -> Dict[str, Any]:
        """データの抽出"""
        for url in urls:
            try:
                data = await self._extraction_manager.extract(url, required_fields)
                if data.validation_score >= THRESHOLDS["validation"]:
                    return data.data
            except ExtractionError as e:
                logger.warning(f"Extraction failed for {url}: {str(e)}")
                continue
        raise NoValidDataError()

    def _validate_data(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> bool:
        """データの検証"""
        return all(
            field in data and data[field] is not None
            for field in required_fields
        )

    async def _handle_error(self) -> None:
        """エラーハンドリング"""
        delay = min(
            self._config["base_delay"] * (2 ** self._retry_count),
            self._config["max_delay"]
        )
        logger.warning(
            f"Retry {self._retry_count + 1} after {delay}s due to {self._last_error}"
        )
        await asyncio.sleep(delay)
```

### 1.2 LLMManager
```python
class LLMManager:
    def __init__(self):
        self._llm = None
        self._prompt_templates = self._load_prompt_templates()

    async def initialize(self) -> None:
        """LLMの初期化"""
        self._llm = await self._setup_llm()

    async def generate_keywords(
        self,
        context: Dict[str, Any]
    ) -> List[str]:
        """検索キーワードの生成"""
        prompt = self._prompt_templates["keyword_generation"].format(**context)
        response = await self._llm.generate(prompt)
        return self._parse_keywords(response)

    async def validate_data(
        self,
        data: Dict[str, Any],
        expected: Dict[str, Any]
    ) -> bool:
        """データの検証"""
        prompt = self._prompt_templates["data_validation"].format(
            data=data,
            expected=expected
        )
        response = await self._llm.generate(prompt)
        return self._parse_validation_result(response)

    def _load_prompt_templates(self) -> Dict[str, str]:
        """プロンプトテンプレートの読み込み"""
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

### 1.3 SearchManager
```python
class SearchManager:
    def __init__(self):
        self._api_key = os.getenv("GOOGLE_API_KEY")
        self._cse_id = os.getenv("CSE_ID")
        self._service = self._setup_service()

    async def search(
        self,
        keywords: List[str],
        options: Dict[str, Any]
    ) -> List[SearchResult]:
        """検索の実行"""
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

    def _calculate_relevance(
        self,
        item: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """関連性スコアの計算"""
        text = f"{item['title']} {item['snippet']}"
        return sum(
            text.lower().count(k.lower()) for k in keywords
        ) / len(keywords)
```

### 1.4 ExtractionManager
```python
class ExtractionManager:
    def __init__(self):
        self._session = aiohttp.ClientSession()
        self._parser = HTMLParser()

    async def extract(
        self,
        url: str,
        target_data: List[str]
    ) -> ExtractedData:
        """データの抽出"""
        try:
            html = await self._fetch_page(url)
            parsed = self._parser.parse(html)
            data = self._extract_target_data(parsed, target_data)
            score = self._calculate_validation_score(data, target_data)
            return ExtractedData(
                data=data,
                metadata={"url": url, "timestamp": datetime.now().isoformat()},
                validation_score=score
            )
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise ExtractionError(str(e))

    async def _fetch_page(self, url: str) -> str:
        """ページの取得"""
        async with self._session.get(url) as response:
            if response.status != 200:
                raise ExtractionError(f"HTTP {response.status}")
            return await response.text()

    def _calculate_validation_score(
        self,
        data: Dict[str, Any],
        target_data: List[str]
    ) -> float:
        """検証スコアの計算"""
        return len([k for k in target_data if k in data]) / len(target_data)
```

## 2. 例外クラス設計

```python
class AdaptiveCrawlerError(Exception):
    """基底例外クラス"""
    pass

class MaxRetriesExceededError(AdaptiveCrawlerError):
    """最大再試行回数超過"""
    pass

class NoValidDataError(AdaptiveCrawlerError):
    """有効なデータなし"""
    pass

class SearchError(AdaptiveCrawlerError):
    """検索エラー"""
    pass

class ExtractionError(AdaptiveCrawlerError):
    """抽出エラー"""
    pass

class ValidationError(AdaptiveCrawlerError):
    """検証エラー"""
    pass
```

## 3. 設定ファイル

### 3.1 config.yaml
```yaml
adaptive_crawler:
  max_attempts: 5
  base_delay: 2
  max_delay: 32
  timeouts:
    llm: 30
    search: 10
    extraction: 45
    total: 90
  thresholds:
    relevance: 0.7
    validation: 0.8
    confidence: 0.6
  site_restrict:
    - "*.release.tdnet.info"
    - "*.jpx.co.jp"
  date_restrict: "m6"  # 過去6ヶ月
```

## 4. ログ設定

### 4.1 logging.yaml
```yaml
version: 1
formatters:
  detailed:
    format: '%(asctime)s %(levelname)s [%(name)s] %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: detailed
    level: INFO
  file:
    class: logging.FileHandler
    filename: logs/adaptive_crawler.log
    formatter: detailed
    level: DEBUG
loggers:
  adaptive_crawler:
    level: DEBUG
    handlers: [console, file]
    propagate: no
```

## 5. メトリクス定義

### 5.1 Prometheus形式
```python
METRICS = {
    "crawl_duration_seconds": Histogram(
        "adaptive_crawler_duration_seconds",
        "クローリング処理の所要時間",
        buckets=[10, 30, 60, 90, 120]
    ),
    "retry_count": Counter(
        "adaptive_crawler_retry_total",
        "再試行回数"
    ),
    "success_rate": Gauge(
        "adaptive_crawler_success_rate",
        "成功率"
    ),
    "error_count": Counter(
        "adaptive_crawler_error_total",
        "エラー数",
        ["error_type"]
    )
}
```

## 6. テスト設計

### 6.1 単体テスト
```python
class TestAdaptiveCrawler:
    @pytest.fixture
    def crawler(self):
        config = load_config("config.yaml")
        return AdaptiveCrawler(config)

    @pytest.mark.asyncio
    async def test_crawl_success(self, crawler):
        result = await crawler.crawl_ir_info("7203", ["financial_results"])
        assert "financial_results" in result
        assert result["financial_results"] is not None

    @pytest.mark.asyncio
    async def test_max_retries(self, crawler):
        with pytest.raises(MaxRetriesExceededError):
            await crawler.crawl_ir_info("0000", ["invalid_field"])
```

### 6.2 統合テスト
```python
class TestIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end(self):
        crawler = AdaptiveCrawler(load_config("config.yaml"))
        result = await crawler.crawl_ir_info(
            "7203",
            ["financial_results", "press_releases"]
        )
        assert all(k in result for k in ["financial_results", "press_releases"])
        assert all(v is not None for v in result.values())
```

## 7. デプロイメント手順

### 7.1 環境変数設定
```bash
export GOOGLE_API_KEY="your-api-key"
export CSE_ID="your-cse-id"
export LOG_LEVEL="INFO"
export CONFIG_PATH="/path/to/config.yaml"
```

### 7.2 依存関係
```toml
[tool.poetry.dependencies]
python = "^3.10"
aiohttp = "^3.8.0"
beautifulsoup4 = "^4.9.3"
google-api-python-client = "^2.0.0"
prometheus-client = "^0.9.0"
pyyaml = "^5.4.1"
``` 