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
└── LLMEvaluator（LLMによる評価）
    ├── PromptGenerator: 評価用プロンプトの生成
    ├── SemanticAnalyzer: 意味解析の実行
    └── ResultsAggregator: 評価結果の集約
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

## 3. 並列処理設計

### 3.1 同時実行制御
```python
class ConcurrencyManager:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = RateLimiter(
            calls_per_second=1.0,
            burst_size=3
        )

    async def execute(self, task: Callable):
        async with self.semaphore:
            async with self.rate_limiter:
                return await task()
```

### 3.2 エラー処理
```python
class ErrorHandler:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.backoff = ExponentialBackoff(
            initial=1.0,
            maximum=30.0
        )

    async def handle_error(self, error: Exception) -> bool:
        """エラーの種類に応じた処理の決定"""
        if isinstance(error, RateLimitError):
            return await self.handle_rate_limit()
        elif isinstance(error, NetworkError):
            return await self.handle_network_error()
        return False
```

## 4. 監視・計測設計

### 4.1 性能指標
- URL評価の実行時間
- LLMリクエストのレイテンシ
- 同時実行数の推移
- エラーレート

### 4.2 精度指標
- 適合率（Precision）の計測
- 再現率（Recall）の計測
- 信頼度スコアの分布
- 誤判定の分析

### 4.3 ログ設計
```python
class AnalysisLogger:
    def log_url_evaluation(
        self,
        url: str,
        result: Dict[str, Any],
        execution_time: float
    ):
        """評価結果とパフォーマンス指標のログ記録"""
        pass

    def log_error(
        self,
        url: str,
        error: Exception,
        context: Dict[str, Any]
    ):
        """エラー情報の詳細なログ記録"""
        pass
``` 