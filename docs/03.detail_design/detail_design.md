# 企業情報クローラー 詳細設計書

## 1. モジュール詳細設計

### 1.1 設定管理モジュール

#### CompanyConfig クラス
```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class CompanyConfig:
    """企業ごとの設定を管理するクラス"""
    base_url: str
    name: str
    paths: Dict[str, str]
    selectors: Dict[str, Dict]
    date_formats: Dict[str, str]
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3
```

#### ConfigLoader クラス
```python
class ConfigLoader:
    """設定ファイルを読み込み、管理するクラス"""
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict = {}
    
    def load_config(self) -> None:
        """YAMLファイルから設定を読み込む"""
        pass
    
    def get_company_config(self, company_code: str) -> CompanyConfig:
        """企業コードに基づいて設定を取得"""
        pass
    
    def validate_config(self) -> bool:
        """設定の妥当性を���証"""
        pass
```

### 1.2 クローラー基盤モジュール

#### BaseCrawler クラス
```python
from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseCrawler(ABC):
    """クローラーの基底クラス"""
    def __init__(self, config: CompanyConfig, monitor: CrawlerMonitor):
        self.config = config
        self.monitor = monitor
        self.session = self._init_session()
    
    def _init_session(self) -> requests.Session:
        """セッションの初期化"""
        pass
    
    @abstractmethod
    def crawl(self) -> Any:
        """クローリングを実行"""
        pass
    
    def make_request(self, url: str) -> Optional[requests.Response]:
        """HTTPリクエストを実行"""
        pass
    
    def handle_error(self, error: Exception) -> None:
        """エラーハンドリング"""
        pass
    
    def update_progress(self, status: str) -> None:
        """進捗状況を更新"""
        pass
```

### 1.3 データ収集モジュール

#### CompanyCrawler クラス
```python
class CompanyCrawler(BaseCrawler):
    """企業情報を収集するクローラー"""
    def crawl(self) -> Dict[str, Any]:
        """企業情報のクローリングを実行"""
        pass
    
    def _parse_company_info(self, html: str) -> Dict[str, Any]:
        """企業情報をパース"""
        pass
```

#### FinancialCrawler クラス
```python
class FinancialCrawler(BaseCrawler):
    """財務情報を収集するクローラー"""
    def crawl(self) -> List[Dict[str, Any]]:
        """財務情報のクローリングを実行"""
        pass
    
    def _parse_financial_info(self, html: str) -> List[Dict[str, Any]]:
        """財務情報をパース"""
        pass
```

#### NewsCrawler クラス
```python
class NewsCrawler(BaseCrawler):
    """ニュース情報を収集するクローラー"""
    def crawl(self) -> List[Dict[str, Any]]:
        """ニュース情報のクローリングを実行"""
        pass
    
    def _parse_news(self, html: str) -> List[Dict[str, Any]]:
        """ニュース情報をパース"""
        pass
```

### 1.4 モニタリングモジュール

#### CrawlerMetrics クラス
```python
@dataclass
class CrawlerMetrics:
    """クローラーのメトリクス情報"""
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    error_count: int = 0
    warning_count: int = 0
    processed_items: int = 0
```

#### CrawlerMonitor クラス
```python
class CrawlerMonitor:
    """クローラーの監視を行うクラス"""
    def __init__(self, company_code: str):
        self.company_code = company_code
        self.metrics = CrawlerMetrics(start_time=datetime.now())
        self.logger = self._init_logger()
    
    def _init_logger(self) -> logging.Logger:
        """ロガーの初期化"""
        pass
    
    def start_crawler(self) -> None:
        """クローラーの開始を記録"""
        pass
    
    def stop_crawler(self) -> None:
        """クローラーの終了を記録"""
        pass
    
    def log_error(self, error: Exception) -> None:
        """エラーを記録"""
        pass
    
    def log_warning(self, message: str) -> None:
        """警告を記録"""
        pass
    
    def update_progress(self, status: str, processed_items: int) -> None:
        """進捗状況を更新"""
        pass
```

### 1.1 企業リスト管理モジュール

#### CompanyList クラス
```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class CompanyListConfig:
    """企業リストの設定"""
    source: str
    update_interval: int
    filters: Dict[str, List[str]]
    validation: Dict[str, int]

class CompanyList:
    """企業リストを管理するクラス"""
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: CompanyListConfig = None
        self.companies: List[str] = []
        self.last_update: Optional[datetime] = None
    
    def load_company_list(self) -> List[str]:
        """企業リストを読み込む"""
        pass
    
    def validate_company_info(self, company_code: str) -> bool:
        """企業情報を検証"""
        pass
    
    def update_company_list(self) -> None:
        """企業リストを更新"""
        pass
    
    def get_target_companies(self, filters: Optional[Dict] = None) -> List[str]:
        """対象企業のリストを取得"""
        pass
```

#### CompanyValidator クラス
```python
class CompanyValidator:
    """企業情報を検証するクラス"""
    def __init__(self, timeout: int = 5, retry_count: int = 3):
        self.timeout = timeout
        self.retry_count = retry_count
    
    def validate_company_code(self, company_code: str) -> bool:
        """企業コードの形式を検証"""
        pass
    
    def validate_company_url(self, url: str) -> bool:
        """企業URLの有効性を検証"""
        pass
    
    def validate_company_status(self, company_code: str) -> bool:
        """企業の状態を検証（上場廃止等）"""
        pass
```

### 1.2 並行処理管理モジュール

#### CrawlerExecutor クラス
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Callable

class CrawlerExecutor:
    """クローラーの並行実行を管理するクラス"""
    def __init__(self, max_workers: int, interval: float):
        self.max_workers = max_workers
        self.interval = interval
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Any] = {}
    
    def submit_task(self, company_code: str, task: Callable) -> None:
        """タスクを実行キューに追加"""
        pass
    
    def wait_for_completion(self) -> Dict[str, Any]:
        """全タスクの完了を待機"""
        pass
    
    def handle_task_result(self, company_code: str, result: Any) -> None:
        """タスク実行結果を処理"""
        pass
    
    def handle_task_error(self, company_code: str, error: Exception) -> None:
        """タスクエラーを処理"""
        pass
```

#### TaskQueue クラス
```python
from queue import PriorityQueue
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    """クローリングタスク"""
    company_code: str
    priority: int
    created_at: datetime
    retries: int = 0
    max_retries: int = 3

class TaskQueue:
    """タスクキューを管理するクラス"""
    def __init__(self):
        self.queue = PriorityQueue()
        self.processing: Dict[str, Task] = {}
    
    def add_task(self, task: Task) -> None:
        """タスクをキューに追加"""
        pass
    
    def get_next_task(self) -> Optional[Task]:
        """次のタスクを取得"""
        pass
    
    def mark_completed(self, company_code: str) -> None:
        """タスクを完了としてマーク"""
        pass
    
    def retry_task(self, company_code: str) -> None:
        """タスクをリトライキューに追加"""
        pass
```

## 2. データベース詳細設計

### 2.1 テーブル定義

#### companies テーブル
| カラム名 | データ型 | NULL | キー | 説明 |
|----------|----------|------|------|------|
| id | INTEGER | NO | PK | 主キー |
| company_code | TEXT | NO | UQ | 企業コード |
| name | TEXT | NO | - | 企業名 |
| stock_exchange | TEXT | NO | - | 上場取引所 |
| industry | TEXT | NO | - | 業種 |
| description | TEXT | YES | - | 企業概要 |

#### financials テーブル
| カラム�� | データ型 | NULL | キー | 説明 |
|----------|----------|------|------|------|
| id | INTEGER | NO | PK | 主キー |
| company_id | INTEGER | NO | FK | 企業ID |
| fiscal_year | INTEGER | NO | - | 会計年度 |
| revenue | REAL | YES | - | 売上高 |
| operating_income | REAL | YES | - | 営業利益 |
| net_income | REAL | YES | - | 純利益 |

#### news テーブル
| カラム名 | データ型 | NULL | キー | 説明 |
|----------|----------|------|------|------|
| id | INTEGER | NO | PK | 主キー |
| company_id | INTEGER | NO | FK | 企業ID |
| title | TEXT | NO | - | タイトル |
| url | TEXT | NO | - | URL |
| published_at | TIMESTAMP | NO | - | 公開日時 |
| source | TEXT | NO | - | 情報ソース |

### 2.2 インデックス定義

```sql
-- companies テーブル
CREATE UNIQUE INDEX idx_companies_code ON companies(company_code);

-- financials テーブル
CREATE INDEX idx_financials_company ON financials(company_id);
CREATE INDEX idx_financials_year ON financials(fiscal_year);

-- news テーブル
CREATE INDEX idx_news_company ON news(company_id);
CREATE INDEX idx_news_published ON news(published_at);
```

## 3. エラーハンドリング詳細

### 3.1 例外クラス
```python
class CrawlerException(Exception):
    """クローラーの基本例外クラス"""
    pass

class ConfigurationError(CrawlerException):
    """設定エラー"""
    pass

class RequestError(CrawlerException):
    """リクエストエラー"""
    pass

class ParseError(CrawlerException):
    """パースエラー"""
    pass
```

### 3.2 エラーハンドリングフロー

1. リクエストエラー
```python
try:
    response = self.make_request(url)
except RequestError as e:
    self.monitor.log_error(e)
    if self.should_retry():
        return self.retry_request(url)
    raise
```

2. パースエラー
```python
try:
    data = self._parse_content(html)
except ParseError as e:
    self.monitor.log_error(e)
    self.monitor.log_warning("Invalid HTML structure")
    return None
```

## 4. 設定ファイル詳細

### 4.1 companies.yaml
```yaml
companies:
  '9843':  # ニトリ
    base_url: "https://www.nitori-hd.co.jp"
    name: "株式会社ニトリホールディングス"
    paths:
      company_info: "/ir/company/"
      financial_info: "/ir/library/result/"
      news: "/ir/news/"
    selectors:
      company_info:
        name: ".company-name"
        stock_exchange: ".stock-exchange"
        industry: ".industry"
        description: ".company-description"
      financial_info:
        table: ".financial-table"
        revenue: "td:nth-child(2)"
        operating_income: "td:nth-child(3)"
        net_income: "td:nth-child(4)"
      news:
        list: ".news-list"
        title: ".news-title"
        url: ".news-link"
        date: ".news-date"
    date_formats:
      news: "%Y年%m月%d日"
    headers:
      User-Agent: "CompanyCrawler/1.0"
    timeout: 30
    max_retries: 3
```

## 5. ログ出力詳細

### 5.1 ログフォーマット
```python
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
```

### 5.2 ログ出力例
```
2024-01-20 10:00:00 [INFO] Starting crawler for company: 9843
2024-01-20 10:00:01 [INFO] Fetching company information
2024-01-20 10:00:02 [WARNING] Slow response time: 2.5s
2024-01-20 10:00:03 [ERROR] Failed to parse financial data: Invalid table structure
2024-01-20 10:00:04 [INFO] Completed crawling for company: 9843
```

## 6. 監視メトリクス詳細

### 6.1 基本メトリクス
- クローリング実行時間
- 成功/失敗回数
- データ取得数
- エラー発生数

### 6.2 パフォーマンスメトリクス
- リクエスト応答時間
- メモリ使用量
- CPU使用率
- 同時実行数

### 6.3 メトリクス収集
```python
def collect_metrics(self) -> Dict[str, Any]:
    """メトリクスを収集"""
    return {
        "execution_time": self.get_execution_time(),
        "success_rate": self.calculate_success_rate(),
        "error_rate": self.calculate_error_rate(),
        "data_count": self.get_data_count()
    }
```

## 7. 並行処理詳細

### 7.1 実行フロー
```python
async def crawl_companies(company_list: List[str]) -> Dict[str, Any]:
    """複数企業のクローリングを実行"""
    executor = CrawlerExecutor(max_workers=5, interval=1.0)
    results = {}
    
    for company_code in company_list:
        task = create_crawling_task(company_code)
        executor.submit_task(company_code, task)
    
    results = await executor.wait_for_completion()
    return results

def create_crawling_task(company_code: str) -> Callable:
    """クローリングタスクを作成"""
    async def task():
        config = load_company_config(company_code)
        crawler = CompanyCrawler(config)
        return await crawler.crawl()
    return task
```

### 7.2 エラーハンドリング
```python
def handle_crawling_error(company_code: str, error: Exception) -> None:
    """クローリングエラーの処理"""
    if isinstance(error, RequestError):
        if should_retry(company_code):
            retry_task(company_code)
        else:
            log_permanent_failure(company_code, error)
    elif isinstance(error, ParseError):
        log_parsing_error(company_code, error)
        notify_admin(company_code, error)
    else:
        log_unexpected_error(company_code, error)
        raise
```

### 7.3 進捗管理
```python
@dataclass
class CrawlingProgress:
    """クローリングの進捗情報"""
    total_companies: int
    completed: int
    failed: int
    in_progress: int
    remaining: int
    start_time: datetime
    estimated_completion: Optional[datetime]

class ProgressTracker:
    """進捗状況を追跡するクラス"""
    def __init__(self, total_companies: int):
        self.total = total_companies
        self.progress = CrawlingProgress(
            total_companies=total_companies,
            completed=0,
            failed=0,
            in_progress=0,
            remaining=total_companies,
            start_time=datetime.now(),
            estimated_completion=None
        )
    
    def update_progress(self, status: str, company_code: str) -> None:
        """進捗状況を更新"""
        pass
    
    def get_progress(self) -> CrawlingProgress:
        """現在の進捗状況を取得"""
        pass
    
    def estimate_completion(self) -> datetime:
        """完了予定時刻を推定"""
        pass
```

## 8. LLM統合詳細設計

### 8.1 LLMインターフェース

#### BaseLLM クラス
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLM(ABC):
    """LLMの基底クラス"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = self._init_client()
    
    @abstractmethod
    def _init_client(self) -> Any:
        """クライアントの初期化"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """テキスト生成"""
        pass
    
    @abstractmethod
    async def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """コンテンツ分析"""
        pass
```

#### GeminiLLM クラス
```python
class GeminiLLM(BaseLLM):
    """Gemini APIを使用するLLM実装"""
    async def generate(self, prompt: str, **kwargs) -> str:
        """テキスト生成の実装"""
        pass
    
    async def analyze(self, content: str, **kwargs) -> Dict[str, Any]:
        """コンテンツ分析の実装"""
        pass
```

### 8.2 LLMマネージャー詳細

#### LLMManager クラス
```python
class LLMManager:
    """LLMの管理を行うクラス"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, BaseLLM] = {}
        self._load_models()
    
    def _load_models(self) -> None:
        """設定に基づいてモデルをロード"""
        for model_config in self.config["available_models"]:
            model = self._create_model_instance(model_config)
            self.models[model_config["name"]] = model
    
    def get_model(self, task: str) -> BaseLLM:
        """タスクに応じたモデルを取得"""
        task_config = self.config["tasks"][task]
        model_name = task_config.get("model", self.config["default_model"])
        return self.models[model_name]
    
    async def generate_selectors(self, html: str) -> Dict[str, str]:
        """HTMLからセレクターを生成"""
        model = self.get_model("selector_generation")
        prompt = self._create_selector_prompt(html)
        response = await model.generate(prompt)
        return self._parse_selector_response(response)
    
    async def extract_content(
        self, html: str, selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """HTMLからコンテンツを抽出"""
        model = self.get_model("content_extraction")
        prompt = self._create_extraction_prompt(html, selectors)
        response = await model.generate(prompt)
        return self._parse_extraction_response(response)
    
    async def analyze_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> str:
        """エラーを分析"""
        model = self.get_model("error_analysis")
        prompt = self._create_error_prompt(error, context)
        response = await model.generate(prompt)
        return self._parse_error_analysis(response)
```

### 8.3 プロンプト管理

#### PromptTemplate クラス
```python
@dataclass
class PromptTemplate:
    """プロンプトテンプレートを管理"""
    template: str
    required_variables: List[str]
    
    def format(self, **kwargs) -> str:
        """テンプレートを整形"""
        missing = set(self.required_variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        return self.template.format(**kwargs)
```

#### PromptManager クラス
```python
class PromptManager:
    """プロンプトの管理を行うクラス"""
    def __init__(self, config_path: str):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates(config_path)
    
    def _load_templates(self, config_path: str) -> None:
        """テンプレートをロード"""
        pass
    
    def get_template(self, task: str) -> PromptTemplate:
        """タスクに応じたテンプレートを取得"""
        pass
    
    def format_prompt(self, task: str, **kwargs) -> str:
        """プロンプトを整形"""
        template = self.get_template(task)
        return template.format(**kwargs)
```

### 8.4 LLMを使用したクローラーの拡張

#### AdaptiveCrawler クラス
```python
class AdaptiveCrawler(BaseCrawler):
    """LLMを活用した適応型クローラー"""
    def __init__(
        self,
        config: CompanyConfig,
        monitor: CrawlerMonitor,
        llm_manager: LLMManager
    ):
        super().__init__(config, monitor)
        self.llm_manager = llm_manager
    
    async def _analyze_page_structure(self, html: str) -> Dict[str, str]:
        """ページ構造を分析してセレクターを生成"""
        return await self.llm_manager.generate_selectors(html)
    
    async def _extract_data(
        self, html: str, selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """データを抽出"""
        return await self.llm_manager.extract_content(html, selectors)
    
    async def _handle_extraction_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> None:
        """抽出エラーを処理"""
        analysis = await self.llm_manager.analyze_error(error, context)
        self.monitor.log_error(error, analysis)
        if "retry" in analysis.lower():
            await self._retry_extraction(context)
```

### 8.5 エラー処理の拡張

#### LLMAssistedErrorHandler クラス
```python
class LLMAssistedErrorHandler:
    """LLMを活用したエラーハンドリング"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """エラーを処理"""
        analysis = await self.llm_manager.analyze_error(error, context)
        if self._should_retry(analysis):
            return await self._execute_retry_strategy(analysis, context)
        return None
    
    def _should_retry(self, analysis: str) -> bool:
        """リトライすべきかを判断"""
        pass
    
    async def _execute_retry_strategy(
        self,
        analysis: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """リトライ戦略を実行"""
        pass
``` 