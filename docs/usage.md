# 使用方法

## 基本的な使用方法

### 1. クローラーの初期化

```python
from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager

# LLMマネージャーを初期化
manager = LLMManager()
manager.load_model('gemini-2.0-flash-exp', 'your-api-key')

# クローラーを初期化
crawler = AdaptiveCrawler(
    company_code='9843',
    llm_manager=manager,
    max_retries=3,
    retry_delay=1.0
)
```

### 2. クロールの実行

```python
# クロール対象のデータを定義
target_data = {
    'company_name': '会社名',
    'established_date': '設立日',
    'business_description': '事業内容'
}

# クロールを実行
result = await crawler.crawl('https://example.com', target_data)
```

### 3. 結果の処理

```python
if result:
    print('会社名:', result['company_name'])
    print('設立日:', result['established_date'])
    print('事業内容:', result['business_description'])
```

## 高度な使用方法

### 1. カスタムバリデーションの追加

```python
async def validate_company_data(data: Dict[str, Any]) -> bool:
    """企業データを検証"""
    rules = {
        'company_name': {
            'type': 'string',
            'required': True,
            'min_length': 1
        },
        'established_date': {
            'type': 'string',
            'pattern': r'^\d{4}年\d{1,2}月\d{1,2}日$'
        }
    }
    return await crawler.validate_data(data, rules)
```

### 2. エラーハンドリングのカスタマイズ

```python
class CustomCrawler(AdaptiveCrawler):
    async def _handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """エラー処理をカスタマイズ"""
        # エラーを分析
        analysis = await self.llm_manager.analyze_error(
            self.default_model,
            str(error)
        )
        
        # エラー情報をログに記録
        self._log_error(
            f'エラー発生: {str(error)}\n'
            f'コンテキスト: {context}\n'
            f'分析結果: {analysis}'
        )
        
        # カスタムの通知を送信
        await self._notify_error(error, analysis)
```

### 3. 並行処理の実装

```python
async def crawl_multiple(urls: List[str], target_data: Dict[str, str]) -> List[Dict[str, Any]]:
    """複数のURLを並行してクロール"""
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(
                crawler.crawl(url, target_data)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    return results
```

## コマンドラインからの実行

### 1. 単一URLのクロール

```bash
python -m app.cli crawl https://example.com \
    --target company_name=会社名 \
    --target established_date=設立日
```

### 2. 複数URLのクロール

```bash
python -m app.cli crawl-batch urls.txt \
    --target company_name=会社名 \
    --target established_date=設立日 \
    --output results.json
```

### 3. 設定ファイルを使用

```bash
python -m app.cli crawl-config config.yaml
```

設定ファイルの例（config.yaml）：
```yaml
urls:
  - https://example.com/company1
  - https://example.com/company2

target_data:
  company_name: 会社名
  established_date: 設立日
  business_description: 事業内容

options:
  max_retries: 3
  retry_delay: 1.0
  timeout: 30
```

## APIの使用方法

### 1. クロールの開始

```bash
curl -X POST http://localhost:8000/crawl \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://example.com",
        "target_data": {
            "company_name": "会社名",
            "established_date": "設立日"
        }
    }'
```

### 2. ステータスの確認

```bash
curl http://localhost:8000/status/task-123456
```

## エラーハンドリング

### 1. 一般的なエラー

- 接続エラー: ネットワークの問題やタイムアウト
- 解析エラー: HTMLの構造が予期しない形式
- 検証エラー: 抽出したデータが期待する形式でない

### 2. エラーへの対応

1. リトライ可能なエラー
   - ネットワークエラー
   - 一時的なサービス停止
   - レート制限

2. リトライ不可能なエラー
   - 認証エラー
   - 権限エラー
   - 無効なURL

### 3. エラーログの確認

```bash
# エラーログの表示
tail -f logs/error.log

# 特定のエラーの検索
grep "ConnectionError" logs/error.log
``` 