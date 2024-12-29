# URL分析詳細設計

## 1. LLM評価システム詳細

### 1.1 LLMクライアント設定
```python
class LLMConfig:
    """LLMの設定"""
    model_name: str = "gpt-4"  # 使用モデル
    temperature: float = 0.3   # 出力の多様性（低めに設定）
    max_tokens: int = 500      # 最大トークン数
    timeout: float = 30.0      # タイムアウト時間
```

### 1.2 プロンプトエンジニアリング
#### システムプロンプト
```
あなたはURL分析の専門家です。
与えられたURLが企業情報ページである可能性を分析し、
その判断根拠と共に結果を返してください。
```

#### Few-shotサンプル
```python
EXAMPLES = [
    {
        "url": "/company/about/",
        "analysis": {
            "relevance_score": 0.95,
            "category": "company_profile",
            "reason": "標準的な企業情報パス構造",
            "confidence": 0.9
        }
    },
    {
        "url": "/ir/financial/",
        "analysis": {
            "relevance_score": 0.8,
            "category": "ir_info",
            "reason": "投資家向け情報を示すパス",
            "confidence": 0.85
        }
    }
]
```

### 1.3 評価ロジック
```python
class URLEvaluator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompt_generator = PromptGenerator()
        self.result_validator = ResultValidator()

    async def evaluate(
        self,
        url_components: URLComponents,
        language_info: LanguageInfo
    ) -> EvaluationResult:
        # プロンプト生成
        prompt = self.prompt_generator.generate(
            url_components,
            language_info,
            EXAMPLES
        )

        # LLM評価実行
        try:
            raw_result = await self.llm.complete(prompt)
            result = self.result_validator.validate(raw_result)
            return result
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return None
```

## 2. 並列処理詳細

### 2.1 URLバッチ処理
```python
class URLBatchProcessor:
    def __init__(
        self,
        concurrency: int = 5,
        batch_size: int = 20
    ):
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.queue = asyncio.Queue()

    async def process_urls(
        self,
        urls: List[str]
    ) -> List[EvaluationResult]:
        # URLをキューに追加
        for url in urls:
            await self.queue.put(url)

        # 処理タスクの作成
        tasks = [
            self._process_batch()
            for _ in range(self.concurrency)
        ]

        # 並列実行
        results = await asyncio.gather(*tasks)
        return self._merge_results(results)
```

### 2.2 レート制限制御
```python
class RateLimiter:
    def __init__(
        self,
        calls_per_minute: int = 60,
        burst_size: int = 10
    ):
        self.calls_per_minute = calls_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst_size,
                self.tokens + time_passed * 
                (self.calls_per_minute / 60.0)
            )

            if self.tokens < 1:
                wait_time = (1 - self.tokens) * 60.0 / self.calls_per_minute
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1
            self.last_update = now
```

## 3. エラーハンドリング詳細

### 3.1 エラー種別と対応
```python
class URLAnalysisError(Exception):
    """基底エラークラス"""
    pass

class NetworkError(URLAnalysisError):
    """ネットワーク関連エラー"""
    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code

class LLMError(URLAnalysisError):
    """LLM評価関連エラー"""
    def __init__(self, message: str, raw_response: Any):
        self.message = message
        self.raw_response = raw_response

class ValidationError(URLAnalysisError):
    """結果検証エラー"""
    def __init__(self, result: Dict, reason: str):
        self.result = result
        self.reason = reason
```

### 3.2 リトライ戦略
```python
class RetryStrategy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.backoff = ExponentialBackoff()

    async def execute_with_retry(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except URLAnalysisError as e:
                last_error = e
                if not self._should_retry(e):
                    break
                await self.backoff.wait(attempt)
        raise last_error
```

## 4. 監視・計測詳細

### 4.1 メトリクス定義
```python
class URLAnalysisMetrics:
    """分析メトリクス"""
    def __init__(self):
        self.total_urls = 0
        self.processed_urls = 0
        self.error_count = 0
        self.processing_times = []
        self.llm_latencies = []
        self.confidence_scores = []

    def record_url_processing(
        self,
        url: str,
        result: Optional[EvaluationResult],
        processing_time: float,
        llm_latency: float
    ):
        """URL処理結果の記録"""
        self.processed_urls += 1
        self.processing_times.append(processing_time)
        self.llm_latencies.append(llm_latency)
        if result:
            self.confidence_scores.append(
                result.confidence
            )
```

### 4.2 レポート生成
```python
class AnalysisReporter:
    """分析レポート生成"""
    def generate_report(
        self,
        metrics: URLAnalysisMetrics
    ) -> Dict[str, Any]:
        return {
            "summary": {
                "total_urls": metrics.total_urls,
                "processed_urls": metrics.processed_urls,
                "success_rate": self._calc_success_rate(metrics),
                "avg_processing_time": self._calc_avg(
                    metrics.processing_times
                ),
                "avg_confidence": self._calc_avg(
                    metrics.confidence_scores
                )
            },
            "performance": {
                "p50_latency": self._calc_percentile(
                    metrics.llm_latencies, 50
                ),
                "p95_latency": self._calc_percentile(
                    metrics.llm_latencies, 95
                ),
                "p99_latency": self._calc_percentile(
                    metrics.llm_latencies, 99
                )
            },
            "quality": {
                "confidence_distribution": 
                    self._calc_distribution(
                        metrics.confidence_scores
                    ),
                "error_rate": metrics.error_count / 
                    metrics.total_urls
            }
        }
``` 