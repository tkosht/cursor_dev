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