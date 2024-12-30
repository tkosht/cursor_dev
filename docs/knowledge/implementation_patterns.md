# 実装パターン集

## 1. 外部接続パターン

### RequestControllerパターン
```python
class RequestController:
    """リクエスト制御を行うパターン"""
    def __init__(self, max_concurrent: int = 5, min_interval: float = 1.0):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.min_interval = min_interval
        self.last_request = {}
        
    async def __aenter__(self):
        await self.semaphore.acquire()
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        self.semaphore.release()
        
    async def wait_if_needed(self, key: str):
        """必要な待機時間を確保"""
        now = time.time()
        if key in self.last_request:
            elapsed = now - self.last_request[key]
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        self.last_request[key] = now
```

### SessionManagerパターン
```python
class SessionManager:
    """HTTPセッション管理を行うパターン"""
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(
            total=60.0,
            connect=20.0,
            sock_read=20.0
        )
        self.headers = {
            "User-Agent": "CustomCrawler/1.0",
            "Accept": "text/html,application/xhtml+xml"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers,
            connector=aiohttp.TCPConnector(
                limit=10,
                enable_cleanup_closed=True
            )
        )
        return self.session
        
    async def __aexit__(self, exc_type, exc, tb):
        if not self.session.closed:
            await self.session.close()
```

### ErrorHandlerパターン
```python
class ErrorHandler:
    """エラー処理を行うパターン"""
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    async def handle_with_retry(self, func, *args, **kwargs):
        """リトライ付きの関数実行"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                continue
```

## 2. テストパターン

### AsyncTestCaseパターン
```python
class AsyncTestCase(unittest.TestCase):
    """非同期テストケース基底クラス"""
    async def asyncSetUp(self):
        """非同期セットアップ"""
        self.session_manager = SessionManager()
        self.session = await self.session_manager.__aenter__()
        
    async def asyncTearDown(self):
        """非同期クリーンアップ"""
        await self.session_manager.__aexit__(None, None, None)
        
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncSetUp())
        
    def tearDown(self):
        self.loop.run_until_complete(self.asyncTearDown())
        self.loop.close()
```

### AsyncTestServerパターン
```python
class AsyncTestServer:
    """テスト用HTTPサーバー"""
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        
    async def __aenter__(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        if self.runner:
            await self.runner.cleanup()
```

## 3. アクセス制御パターン

### DomainFilterパターン
```python
class DomainFilter:
    """ドメインフィルタリングを行うパターン"""
    def __init__(self, allowed_domains: Set[str]):
        self.allowed_domains = allowed_domains
        
    def is_allowed(self, url: str) -> bool:
        """URLのアクセス可否を判定"""
        domain = urlparse(url).netloc
        return domain in self.allowed_domains
        
    def add_domain(self, domain: str):
        """許可ドメインの追加"""
        self.allowed_domains.add(domain)
```

### ConfigurationManagerパターン
```python
class ConfigurationManager:
    """設定管理を行うパターン"""
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """設定ファイルの読み込み"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)
            
    def get_timeout(self) -> int:
        """タイムアウト値の取得"""
        return self.config.get("timeout", 60)
        
    def get_max_retries(self) -> int:
        """最大リトライ回数の取得"""
        return self.config.get("max_retries", 3)
```

## 4. データ処理パターン

### DataExtractorパターン
```python
class DataExtractor:
    """データ抽出を行うパターン"""
    def extract_financial_data(self, html: str) -> Dict:
        """財務データの抽出"""
        soup = BeautifulSoup(html, "html.parser")
        data = {}
        
        # 売上高
        revenue = soup.select_one(".revenue")
        if revenue:
            data["revenue"] = self._parse_number(revenue.text)
            
        # 営業利益
        operating_income = soup.select_one(".operating-income")
        if operating_income:
            data["operating_income"] = self._parse_number(operating_income.text)
            
        return data
        
    def _parse_number(self, text: str) -> Optional[float]:
        """数値のパース"""
        try:
            return float(re.sub(r"[^\d.-]", "", text))
        except ValueError:
            return None
```

### DataValidatorパターン
```python
class DataValidator:
    """データ検証を行うパターン"""
    def validate_financial_data(self, data: Dict) -> bool:
        """財務データの検証"""
        required_fields = {"revenue", "operating_income"}
        
        # 必須フィールドの存在確認
        if not all(field in data for field in required_fields):
            return False
            
        # 数値の妥当性確認
        for field in required_fields:
            value = data[field]
            if not isinstance(value, (int, float)) or value < 0:
                return False
                
        return True
```

## 5. AdaptiveCrawlerパターン

### SelectorGeneratorパターン
```python
class SelectorGenerator:
    """LLMを使用してセレクタを生成するパターン"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        
    async def generate_selectors(self, html: str, target_data: str) -> List[str]:
        """HTMLからデータ抽出用のセレクタを生成"""
        # HTMLの構造を解析
        soup = BeautifulSoup(html, "html.parser")
        structure = self._extract_structure(soup)
        
        # LLMにプロンプトを送信
        prompt = self._create_prompt(structure, target_data)
        response = await self.llm_manager.generate_selectors(prompt)
        
        # 候補を優先順位付けして返却
        return self._prioritize_selectors(response)
        
    def _extract_structure(self, soup: BeautifulSoup) -> str:
        """HTMLの重要な構造を抽出"""
        # テーブル、見出し、特徴的なクラス名などを抽出
        tables = soup.find_all("table")
        headings = soup.find_all(["h1", "h2", "h3"])
        return self._format_structure(tables, headings)
        
    def _create_prompt(self, structure: str, target_data: str) -> str:
        """LLM用のプロンプトを生成"""
        return f"""
        以下のHTML構造から{target_data}を抽出するための
        CSSセレクタを複数提案してください。
        優先順位も付けてください。

        HTML構造:
        {structure}
        """
        
    def _prioritize_selectors(self, response: str) -> List[str]:
        """セレクタに優先順位を付ける"""
        selectors = response.split("\n")
        # 具体的なセレクタを優先
        return sorted(selectors, key=lambda s: self._calculate_priority(s))
```

### FinancialDataExtractorパターン
```python
class FinancialDataExtractor:
    """財務データ抽出を行うパターン"""
    def __init__(self):
        self.date_parser = DateParser()
        self.number_parser = NumberParser()
        
    def extract_data(self, html: str, selectors: List[str]) -> Dict:
        """財務データを抽出"""
        soup = BeautifulSoup(html, "html.parser")
        data = {}
        
        for field, selector_list in selectors.items():
            for selector in selector_list:
                element = soup.select_one(selector)
                if element:
                    value = self._parse_value(element.text, field)
                    if value is not None:
                        data[field] = value
                        break
                        
        return data
        
    def _parse_value(self, text: str, field_type: str) -> Optional[Union[float, str, date]]:
        """フィールドの種類に応じた値のパース"""
        if field_type in {"revenue", "operating_income", "net_income"}:
            return self.number_parser.parse(text)
        elif field_type in {"announcement_date", "release_date"}:
            return self.date_parser.parse(text)
        else:
            return text.strip()
```

### NewsExtractorパターン
```python
class NewsExtractor:
    """ニュース記事抽出を行うパターン"""
    def __init__(self):
        self.date_parser = DateParser()
        
    def extract_news(self, html: str, selectors: Dict[str, List[str]]) -> List[Dict]:
        """ニュース記事のリストを抽出"""
        soup = BeautifulSoup(html, "html.parser")
        news_list = []
        
        # ニュース一覧の要素を取得
        for list_selector in selectors["news_list"]:
            news_elements = soup.select(list_selector)
            if news_elements:
                for element in news_elements:
                    news = self._extract_news_item(
                        element,
                        selectors["title"],
                        selectors["date"],
                        selectors["url"]
                    )
                    if news:
                        news_list.append(news)
                break
                
        return news_list
        
    def _extract_news_item(
        self,
        element: Tag,
        title_selectors: List[str],
        date_selectors: List[str],
        url_selectors: List[str]
    ) -> Optional[Dict]:
        """個別のニュース記事を抽出"""
        news = {}
        
        # タイトルの抽出
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                news["title"] = title_elem.text.strip()
                break
                
        # 日付の抽出
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                news["date"] = self.date_parser.parse(date_elem.text)
                break
                
        # URLの抽出
        for selector in url_selectors:
            url_elem = element.select_one(selector)
            if url_elem and url_elem.has_attr("href"):
                news["url"] = url_elem["href"]
                break
                
        return news if len(news) == 3 else None
```

### DateParserパターン
```python
class DateParser:
    """日付パースを行うパターン"""
    def __init__(self):
        self.patterns = [
            r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})",  # 2024-01-01, 2024/01/01, 2024年1月1日
            r"(\d{4})(\d{2})(\d{2})",                   # 20240101
            r"(\d{2})[-/月](\d{1,2})",                  # 01-01, 01/01, 1月1日（今年）
        ]
        
    def parse(self, text: str) -> Optional[date]:
        """日付文字列をパース"""
        text = self._normalize(text)
        
        for pattern in self.patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return self._convert_to_date(match)
                except ValueError:
                    continue
                    
        return None
        
    def _normalize(self, text: str) -> str:
        """日付文字列を正規化"""
        # 全角数字を半角に変換
        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        # 余分な空白を削除
        return text.strip()
        
    def _convert_to_date(self, match: re.Match) -> date:
        """マッチした値をdate型に変換"""
        groups = match.groups()
        if len(groups) == 3:
            year, month, day = map(int, groups)
            if year < 100:
                year += 2000
        else:
            today = date.today()
            year = today.year
            month, day = map(int, groups)
            
        return date(year, month, day)
```

### NumberParserパターン
```python
class NumberParser:
    """数値パースを行うパターン"""
    def __init__(self):
        self.unit_map = {
            "百万": 1_000_000,
            "億": 100_000_000,
            "兆": 1_000_000_000_000,
            "M": 1_000_000,
            "B": 1_000_000_000,
            "T": 1_000_000_000_000,
        }
        
    def parse(self, text: str) -> Optional[float]:
        """数値文字列をパース"""
        try:
            text = self._normalize(text)
            number = self._extract_number(text)
            unit = self._extract_unit(text)
            return number * (self.unit_map.get(unit, 1))
        except (ValueError, TypeError):
            return None
            
    def _normalize(self, text: str) -> str:
        """数値文字列を正規化"""
        # 全角数字・記号を半角に変換
        text = text.translate(str.maketrans("０１２３４５６７８９－．", "0123456789-."))
        # カンマを除去
        text = text.replace(",", "")
        return text.strip()
        
    def _extract_number(self, text: str) -> float:
        """数値部分を抽出"""
        match = re.search(r"-?\d+\.?\d*", text)
        if match:
            return float(match.group())
        raise ValueError("No number found")
        
    def _extract_unit(self, text: str) -> Optional[str]:
        """単位を抽出"""
        for unit in self.unit_map.keys():
            if unit in text:
                return unit
        return None
```

### LLMOptimizationパターン
```python
class LLMOptimizer:
    """LLMの応答品質を最適化するパターン"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        
    async def optimize_selector_generation(
        self,
        html: str,
        target_data: Dict[str, str]
    ) -> Dict[str, str]:
        """セレクタ生成の最適化"""
        # HTMLの構造を解析
        soup = BeautifulSoup(html, "html.parser")
        
        # LLMにコンテキストを提供
        context = {
            "page_title": soup.title.string if soup.title else "",
            "headings": [h.text for h in soup.find_all(["h1", "h2", "h3"])],
            "tables": len(soup.find_all("table")),
            "target_fields": list(target_data.keys())
        }
        
        # セレクタを生成
        selectors = await self.llm_manager.generate_selectors(
            soup,
            target_data,
            context=context
        )
        
        # 生成されたセレクタを検証
        validated_selectors = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements and self._validate_element_content(
                elements[0],
                target_data[key]
            ):
                validated_selectors[key] = selector
        
        return validated_selectors
        
    def _validate_element_content(
        self,
        element: Tag,
        expected_type: str
    ) -> bool:
        """要素の内容を検証"""
        text = element.get_text(strip=True)
        if "金額" in expected_type or "円" in expected_type:
            return bool(re.search(r'\d+', text))
        elif "日付" in expected_type:
            return bool(re.search(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', text))
        return True

### ConcurrencyControlパターン
```python
class ConcurrencyController:
    """並行処理を制御するパターン"""
    def __init__(
        self,
        max_concurrent: int = 5,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        
    async def execute_with_control(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """制御付きで関数を実行"""
        async with self.semaphore:
            retry_count = 0
            while retry_count <= self.max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    if retry_count > self.max_retries:
                        raise
                    delay = self.retry_delay * (2 ** (retry_count - 1))
                    await asyncio.sleep(delay)
        
    async def execute_batch(
        self,
        tasks: List[Tuple[Callable, tuple, dict]]
    ) -> List[Any]:
        """バッチ処理を実行"""
        async def wrapped_task(func, args, kwargs):
            return await self.execute_with_control(func, *args, **kwargs)
            
        return await asyncio.gather(*[
            wrapped_task(f, args, kwargs)
            for f, args, kwargs in tasks
        ])
```

"""
# IRサイトクローリングパターン

## 実サイトテストパターン

### 概要
実在するIRサイトを使用したテストパターン。モックやスタブを使用せず、実際の外部接続を行う。

### 実装例
```python
@pytest.mark.asyncio
async def test_real_ir_site():
    # 1. クローラーの初期化
    crawler = AdaptiveCrawler(
        company_code="7203",  # 実在する企業コード
        retry_delay=1.0,
        max_concurrent=2,
        timeout_total=30,
        timeout_connect=10,
        timeout_read=20,
        max_retries=3
    )

    # 2. 対象データの定義
    target_data = {
        "revenue": "売上高",
        "operating_profit": "営業利益",
        "net_income": "当期純利益"
    }

    try:
        # 3. クローラーの実行
        async with crawler:
            data = await crawler.crawl(
                "https://real-ir-site.co.jp/financial",
                target_data
            )

        # 4. データの検証
        assert "revenue" in data
        assert isinstance(data["revenue"], str)
        assert "円" in data["revenue"]
        
    except Exception as e:
        logger.error(f"クロール失敗: {str(e)}")
        raise
```

### 利用シーン
- 実際のIRサイトからのデータ抽出テスト
- エラーハンドリングの検証
- パフォーマンステスト

### 注意点
1. レート制限への配慮
   - 適切な待機時間の設定
   - 同時接続数の制限

2. エラー処理
   - ネットワークエラー
   - タイムアウト
   - HTMLパース失敗

3. データ検証
   - 実データとの整合性
   - 形式の妥当性
   - 必須項目の存在確認
""" 

# IR情報クローリングの実装パターン

## LLMを使用したURL解析パターン
```python
class LLMManager:
    async def find_ir_pages(self, base_url: str) -> List[str]:
        """メインサイトからIRページを探索"""
        # 1. ベースURLからリンクを収集
        # 2. 各リンクの関連性をLLMで評価
        # 3. スコアに基づいてフィルタリング
        pass

    async def analyze_ir_content(self, url: str, content: str) -> Dict[str, float]:
        """IR情報の品質を評価"""
        # 1. コンテンツの関連性を評価
        # 2. データの完全性をチェック
        # 3. 信頼度スコアを計算
        pass

    async def select_optimal_ir_page(
        self, candidates: List[str]
    ) -> Tuple[str, float]:
        """最適なIRページを選択"""
        # 1. 各候補ページを評価
        # 2. スコアを比較
        # 3. 最適なページを返却
        pass
```

## アダプティブクローラーパターン
```python
class AdaptiveCrawler:
    async def discover_ir_urls(self, base_url: str) -> List[str]:
        """IRページのURLを自動発見"""
        # 1. サイトマップを取得
        # 2. LLMでURLを評価
        # 3. 候補URLをフィルタリング
        pass

    async def validate_ir_page(self, url: str) -> bool:
        """IRページの妥当性を検証"""
        # 1. ページを取得
        # 2. コンテンツを解析
        # 3. LLMで評価
        pass
```

## エラーハンドリングパターン
```python
async def resilient_crawl(self, url: str) -> Dict[str, Any]:
    """耐障害性のあるクロール処理"""
    retry_count = 0
    while retry_count <= self.max_retries:
        try:
            # 1. ページ取得を試行
            # 2. 成功したら処理を実行
            # 3. 結果を返却
            pass
        except Exception as e:
            # 1. エラーをログに記録
            # 2. リトライ回数をインクリメント
            # 3. 待機時間を計算して待機
            pass
```

## 並行処理制御パターン
```python
class ConcurrencyManager:
    def __init__(self, max_concurrent: int = 5):
        """並行処理の制御を初期化"""
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        """コンテキスト開始"""
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """コンテキスト終了"""
        self.semaphore.release()
``` 