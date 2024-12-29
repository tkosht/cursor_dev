# URL分析基本設計

## 1. システム構成

### 1.1 コンポーネント構成
```
SiteAnalyzer
├── URLCollector（URLの収集）
│   ├── SitemapParser: サイトマップからのURL抽出
│   ├── NavigationExtractor: ナビゲーションからのURL抽出
│   └── URLDeduplicator: URL重複除去
│
├── URLAnalyzer（URL分析）
│   ├── URLStructureAnalyzer: URLの構造解析
│   ├── LanguageDetector: 言語情報の検出
│   └── DomainFilter: 外部ドメインのフィルタリング
│
├── LLMEvaluator（LLMによる評価）
│   ├── PromptGenerator: 評価用プロンプトの生成
│   ├── SemanticAnalyzer: 意味解析の実行
│   └── ResultsAggregator: 評価結果の集約
│
├── ErrorHandler（エラー処理）
│   ├── RetryManager: リトライ制御
│   ├── FallbackStrategy: 代替処理
│   └── ErrorLogger: エラー記録
│
└── MetricsCollector（メトリクス収集）
    ├── PerformanceMonitor: 性能監視
    ├── QualityAnalyzer: 品質分析
    └── MetricsReporter: レポート生成
```

### 1.2 データフロー
1. URLの収集フェーズ
   ```mermaid
   graph LR
   A[Webサイト] --> B[SitemapParser]
   A --> C[NavigationExtractor]
   B --> D[URLDeduplicator]
   C --> D
   ```

2. URL分析フェーズ
   ```mermaid
   graph LR
   D[収集済URL] --> E[URLStructureAnalyzer]
   E --> F[LanguageDetector]
   F --> G[DomainFilter]
   ```

3. LLM評価フェーズ
   ```mermaid
   graph LR
   G[フィルタ済URL] --> H[PromptGenerator]
   H --> I[SemanticAnalyzer]
   I --> J[ResultsAggregator]
   ```

## 2. 機能設計

### 2.1 URL収集機能
- SitemapParser
  - robots.txtからのサイトマップ位置の特定
  - XMLサイトマップの解析
  - 再帰的なサイトマップインデックスの処理

- NavigationExtractor
  - メインナビゲーション要素の特定
  - フッターリンクの抽出
  - アンカータグの正規化

- URLDeduplicator
  - 正規化ルール（末尾スラッシュ、大文字小文字等）
  - 重複判定ロジック
  - URL優先順位付け

### 2.2 URL分析機能
- URLStructureAnalyzer
  ```python
  class URLComponents:
      path_segments: List[str]      # パス部分の分解
      query_params: Dict[str, str]  # クエリパラメータ
      fragment: Optional[str]       # フラグメント
      file_extension: Optional[str] # ファイル拡張子
  ```

- LanguageDetector
  ```python
  class LanguageInfo:
      primary_language: str    # 主要言語
      other_languages: List[str] # 他の対応言語
      confidence: float        # 判定信頼度
  ```

- DomainFilter
  - 同一ドメインチェック
  - サブドメイン処理ルール
  - 許可ドメインリスト

### 2.3 LLM評価機能
- PromptGenerator
  ```python
  def generate_prompt(url_components: URLComponents, language_info: LanguageInfo) -> str:
      """
      評価用プロンプトの生成
      
      プロンプトテンプレート:
      ---
      タスク: 以下のURLが企業情報ページである可能性を評価
      
      URL情報:
      - パス: {path_segments}
      - パラメータ: {query_params}
      - 言語: {language_info}
      
      評価項目:
      1. 各パスセグメントの意味（企業情報関連性）
      2. URLパターンの一般的な用途
      3. 想定されるコンテンツタイプ
      
      出力形式:
      {
          "relevance_score": float,  # 関連性スコア（0-1）
          "category": str,           # ページカテゴリ
          "reason": str,             # 判断理由
          "confidence": float        # 判定信頼度（0-1）
      }
      ---
      """
  ```

- SemanticAnalyzer
  - LLMクライアントの初期化と管理
  - リクエストのレート制限
  - エラーハンドリング
  - 再試行ロジック

- ResultsAggregator
  - スコアの正規化
  - 結果の検証（異常値検出）
  - 信頼度に基づくフィルタリング

### 2.4 エラー処理機能
- RetryManager
  ```python
  class RetryStrategy:
      """リトライ戦略の実装"""
      def __init__(
          self,
          max_retries: int = 3,
          initial_delay: float = 1.0,
          max_delay: float = 30.0,
          jitter: float = 0.1
      ):
          self.max_retries = max_retries
          self.backoff = ExponentialBackoff(
              initial=initial_delay,
              maximum=max_delay,
              jitter=jitter
          )

      async def execute(
          self,
          operation: Callable,
          error_handler: ErrorHandler
      ) -> Any:
          """リトライ付きで処理を実行"""
          for attempt in range(self.max_retries):
              try:
                  return await operation()
              except Exception as e:
                  if not await error_handler.should_retry(e):
                      raise
                  delay = self.backoff.get_delay(attempt)
                  await asyncio.sleep(delay)
          raise MaxRetriesExceededError()
  ```

- FallbackStrategy
  ```python
  class FallbackStrategy:
      """代替処理戦略の実装"""
      async def execute_with_fallback(
          self,
          primary_operation: Callable,
          fallback_operations: List[Callable]
      ) -> Any:
          """代替処理を含めて実行"""
          try:
              return await primary_operation()
          except Exception as primary_error:
              for fallback_op in fallback_operations:
                  try:
                      return await fallback_op()
                  except Exception:
                      continue
              raise primary_error
  ```

- ErrorLogger
  ```python
  class ErrorLogger:
      """エラーログ管理"""
      def __init__(self):
          self.error_counts = Counter()
          self.error_details = defaultdict(list)

      def log_error(
          self,
          error: Exception,
          context: Dict[str, Any]
      ):
          """エラー情報の記録"""
          error_type = type(error).__name__
          self.error_counts[error_type] += 1
          self.error_details[error_type].append({
              "timestamp": time.time(),
              "error": str(error),
              "context": context
          })

      def get_error_summary(self) -> Dict[str, Any]:
          """エラーサマリーの取得"""
          return {
              "counts": dict(self.error_counts),
              "rates": {
                  error_type: count / sum(self.error_counts.values())
                  for error_type, count in self.error_counts.items()
              }
          }
  ```

### 2.5 メトリクス収集機能
- PerformanceMonitor
  ```python
  class PerformanceMetrics:
      """性能指標の収集"""
      def __init__(self):
          self.processing_times = []
          self.llm_latencies = []
          self.concurrent_requests = 0

      def record_processing_time(
          self,
          operation: str,
          duration: float
      ):
          """処理時間の記録"""
          self.processing_times.append({
              "operation": operation,
              "duration": duration,
              "timestamp": time.time()
          })

      def get_performance_summary(self) -> Dict[str, Any]:
          """性能サマリーの取得"""
          return {
              "processing_time": {
                  "p50": np.percentile([p["duration"] for p in self.processing_times], 50),
                  "p95": np.percentile([p["duration"] for p in self.processing_times], 95),
                  "p99": np.percentile([p["duration"] for p in self.processing_times], 99)
              },
              "concurrent_requests": self.concurrent_requests
          }
  ```

- QualityAnalyzer
  ```python
  class QualityMetrics:
      """品質指標の収集"""
      def __init__(self):
          self.relevance_scores = []
          self.confidence_scores = []
          self.category_counts = Counter()

      def record_evaluation_result(
          self,
          result: Dict[str, Any]
      ):
          """評価結果の記録"""
          self.relevance_scores.append(result["relevance_score"])
          self.confidence_scores.append(result["confidence"])
          self.category_counts[result["category"]] += 1

      def get_quality_summary(self) -> Dict[str, Any]:
          """品質サマリーの取得"""
          return {
              "relevance_score": {
                  "mean": np.mean(self.relevance_scores),
                  "std": np.std(self.relevance_scores)
              },
              "confidence_score": {
                  "mean": np.mean(self.confidence_scores),
                  "std": np.std(self.confidence_scores)
              },
              "category_distribution": dict(self.category_counts)
          }
  ```

- MetricsReporter
  ```python
  class MetricsReporter:
      """メトリクスレポートの生成"""
      def __init__(
          self,
          performance_monitor: PerformanceMonitor,
          quality_analyzer: QualityAnalyzer,
          error_logger: ErrorLogger
      ):
          self.performance_monitor = performance_monitor
          self.quality_analyzer = quality_analyzer
          self.error_logger = error_logger

      def generate_report(self) -> Dict[str, Any]:
          """総合レポートの生成"""
          return {
              "performance": self.performance_monitor.get_performance_summary(),
              "quality": self.quality_analyzer.get_quality_summary(),
              "errors": self.error_logger.get_error_summary(),
              "timestamp": time.time()
          }
  ```

## 3. 性能最適化設計

### 3.1 URL構造解析の最適化
- 正規表現のコンパイル済みパターン使用
- URLパース結果のメモリ内キャッシュ
- バッチ処理による効率化

### 3.2 LLMリクエストの最適化
- プロンプトテンプレートの事前コンパイル
- バッチリクエストの活用
- コンテキスト長の最適化

### 3.3 並列処理の最適化
- 動的な同時実行数調整
- I/O待ちの最小化
- メモリ使用量の制御

## 4. 監視・アラート設計

### 4.1 監視項目
- システムメトリクス
  - CPU使用率
  - メモリ使用量
  - ディスクI/O
  - ネットワークI/O

- アプリケーションメトリクス
  - 処理時間
  - エラー率
  - 成功率
  - スループット

- 品質メトリクス
  - 関連性スコア分布
  - 信頼度スコア分布
  - カテゴリ分布

### 4.2 アラート条件
- エラー率 > 5%
- P95処理時間 > 5秒
- 信頼度スコア < 0.8
- 同時実行数 > 5

### 4.3 レポート生成
- リアルタイムダッシュボード
- 日次サマリーレポート
- 週次品質レポート
- 月次総合レポート 