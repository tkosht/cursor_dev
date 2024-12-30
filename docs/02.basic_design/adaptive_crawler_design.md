# AdaptiveCrawler基本設計

## 1. システム構成

### 1.1 主要コンポーネント
- AdaptiveCrawler: クローラーのメインクラス
- LLMManager: LLMとの連携を管理
- AccessController: アクセス制御を管理
- ErrorHandler: エラー処理を管理

### 1.2 外部依存
- aiohttp: HTTP通信
- beautifulsoup4: HTML解析
- OpenAI API: LLMサービス

## 2. クラス設計

### 2.1 AdaptiveCrawler
```python
class AdaptiveCrawler:
    def __init__(self, company_code: str, llm_manager: LLMManager):
        self.company_code = company_code
        self.llm_manager = llm_manager
        self.access_controller = AccessController()
        self.error_handler = ErrorHandler()
        
    async def crawl(self, url: str, data_type: Union[Financial, News]) -> Dict:
        # アクセス制御チェック
        await self.access_controller.check_access(url)
        
        # クロール実行
        try:
            async with self._create_session() as session:
                return await self._execute_crawl(session, url, data_type)
        except Exception as e:
            return await self.error_handler.handle(e)
```

### 2.2 AccessController
```python
class AccessController:
    def __init__(self):
        self.last_access_times: Dict[str, datetime] = {}
        self.semaphore = asyncio.Semaphore(5)
        
    async def check_access(self, url: str):
        # 同一URLへのアクセス間隔チェック
        last_time = self.last_access_times.get(url)
        if last_time and (datetime.now() - last_time).seconds < 3600:
            raise TooFrequentAccessError(url)
            
        # 同時接続数制御
        await self.semaphore.acquire()
```

### 2.3 ErrorHandler
```python
class ErrorHandler:
    def __init__(self):
        self.max_retries = 3
        
    async def handle(self, error: Exception) -> Dict:
        if isinstance(error, aiohttp.ClientError):
            return await self._handle_network_error(error)
        elif isinstance(error, TooFrequentAccessError):
            return await self._handle_access_error(error)
        else:
            return await self._handle_unknown_error(error)
```

## 3. 処理フロー

### 3.1 クロール処理
1. アクセス制御チェック
2. HTTPセッション作成
3. ページ取得
4. コンテンツ解析
5. データ構造化
6. 結果返却

### 3.2 エラー処理フロー
1. エラー種別の判定
2. リトライ判定
3. バックオフ時間の計算
4. リトライ実行
5. 最終エラー処理

## 4. エラー定義

### 4.1 カスタムエラー
```python
class TooFrequentAccessError(Exception):
    """アクセス頻度制限違反エラー"""
    
class ContentParseError(Exception):
    """コンテンツ解析エラー"""
    
class RateLimitError(Exception):
    """レート制限エラー"""
```

## 5. 監視・ログ設計

### 5.1 ログ項目
- アクセス日時
- URL
- 処理時間
- エラー情報
- リトライ回数
- ステータスコード

### 5.2 メトリクス
- 成功率
- 平均処理時間
- エラー発生率
- リトライ率 