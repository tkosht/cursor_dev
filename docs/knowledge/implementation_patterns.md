# 実装パターンと具体的な知見

このドキュメントには、プロジェクト全体で活用できる具体的な実装パターンと知見をまとめています。
これらのパターンは、多くのプロジェクトで再利用可能で、コードの品質と保守性を高めることができます。

## 1. プロジェクト設計・実装パターン

### 1.1 設定管理のベストプラクティス

```python
# 悪い例：ハードコードされた設定
class Crawler:
    BASE_URL = "https://example.com"
    TIMEOUT = 30

# 良い例：外部化された設定
from pydantic import BaseSettings

class CrawlerSettings(BaseSettings):
    base_url: str
    timeout: int = 30
    
    class Config:
        env_prefix = "CRAWLER_"
        env_file = ".env"
```

**利点**:
- 環境ごとの設定変更が容易
- 設定値の型チェックが可能
- 環境変数との連携が簡単
- テスト時の設定変更が容易

### 1.2 エラーハンドリングの具体的パターン

```python
async def fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数バックオフ
```

**利点**:
- 一時的な障害に対する耐性
- 指数バックオフによるサーバー負荷の軽減
- 明確なエラー伝播

### 1.3 非同期処理のパターン

```python
async def process_urls(self, urls: List[str]) -> List[Dict]:
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(self.fetch_url(session, url))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

**利点**:
- リソースの効率的な利用
- セッションの適切な管理
- エラーの適切な処理

## 2. テスト設計パターン

### 2.1 テストケースの構造化

```python
@pytest.mark.asyncio
class TestCrawler:
    @pytest.fixture
    async def crawler(self):
        async with Crawler() as crawler:
            yield crawler

    @pytest.mark.parametrize("url,expected", [
        ("https://valid.com", True),
        ("https://invalid.com", False),
    ])
    async def test_url_validation(self, crawler, url, expected):
        assert await crawler.is_valid_url(url) == expected
```

**利点**:
- テストの再利用性が高い
- パラメータ化によるテストケースの網羅
- フィクスチャによるセットアップの一元管理

### 2.2 モック使用の具体例

```python
def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_response.status_code = 200
    
    mocker.patch('requests.get', return_value=mock_response)
    result = api_client.get_data()
    assert result["status"] == "success"
```

**利点**:
- 外部依存のない安定したテスト
- テスト実行の高速化
- エッジケースのテストが容易

## 3. データベース操作パターン

### 3.1 SQLAlchemyモデル定義

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Company(BaseModel):
    __tablename__ = "companies"
    
    name = Column(String(100), nullable=False, index=True)
    url = Column(String(200), unique=True)
```

**利点**:
- 共通フィールドの一元管理
- 監査フィールドの自動更新
- インデックスの適切な設定

## 4. ログ管理パターン

### 4.1 構造化ログの実装

```python
import structlog

logger = structlog.get_logger()

async def process_data(data: Dict):
    logger.info("processing_started", 
                data_size=len(data),
                timestamp=datetime.now().isoformat())
    try:
        result = await process(data)
        logger.info("processing_completed",
                   result_size=len(result),
                   duration=time.time() - start_time)
        return result
    except Exception as e:
        logger.error("processing_failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise
```

**利点**:
- ログの検索性向上
- メトリクスの収集が容易
- エラー分析の効率化

## 5. パフォーマンス最適化パターン

### 5.1 キャッシュ実装

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str, ttl: int = 300):
        if key in self.cache:
            if datetime.now() - self.timestamps[key] < timedelta(seconds=ttl):
                return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
```

**利点**:
- パフォーマンスの向上
- サーバー負荷の軽減
- TTLによるメモリ管理

## 6. セキュリティ対策パターン

### 6.1 APIキー管理

```python
from pydantic import BaseSettings, SecretStr

class APISettings(BaseSettings):
    api_key: SecretStr
    api_secret: SecretStr
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = APISettings()
headers = {"Authorization": f"Bearer {settings.api_key.get_secret_value()}"}
```

**利点**:
- 機密情報の安全な管理
- 設定の一元化
- 環境変数との連携

## 注意事項

1. これらのパターンは、プロジェクトの要件や制約に応じて適切にカスタマイズする必要があります。
2. パターンを適用する際は、チームメンバーと十分な議論を行い、合意を得ることが重要です。
3. 定期的にパターンの有効性を評価し、必要に応じて改善を行ってください。 