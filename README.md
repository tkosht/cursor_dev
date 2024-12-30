# Adaptive Web Crawler

LLMを使用した適応型Webクローラー

## 概要

このプロジェクトは、LLM（Large Language Model）を使用して、Webページの構造を分析し、動的にセレクタを生成するWebクローラーです。
従来のクローラーとは異なり、HTMLの構造が変更されても自動的に適応することができます。

### 主な機能

- LLMを使用したページ構造の分析
- 動的なセレクタの生成
- データの抽出と検証
- エラー分析と自動リトライ
- 並行処理とパフォーマンス最適化

## セットアップ

### 必要条件

- Python 3.10以上
- Poetry
- Google Cloud Platform（Gemini API）またはOpenAI（GPT-4 API）のAPIキー

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/adaptive-web-crawler.git
cd adaptive-web-crawler
```

2. 依存パッケージをインストール
```bash
make install
```

3. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## 使用方法

### 基本的な使用方法

```python
from app.crawlers.adaptive import AdaptiveCrawler
from app.llm.manager import LLMManager

# LLMマネージャーを初期化
manager = LLMManager()
manager.load_model('gemini-2.0-flash-exp', 'your-api-key')

# クローラーを初期化
crawler = AdaptiveCrawler(
    company_code='9843',
    llm_manager=manager
)

# クロール実行
target_data = {
    'company_name': '会社名',
    'established_date': '設立日',
    'business_description': '事業内容'
}
result = await crawler.crawl('https://example.com', target_data)
```

### コマンドライン実行

```bash
# アプリケーションを実行
make run

# テストを実行
make test  # ユニットテスト
make test-integration  # 統合テスト
make test-all  # 全てのテスト

# コードをチェック
make lint

# コードをフォーマット
make format

# カバレッジレポートを生成
make coverage
```

## 実装の詳細

### URLコレクター

`URLCollector`クラスは、Webサイトからリンクを効率的に収集するための機能を提供します。

#### 主な機能

1. ナビゲーションメニューからのURL収集
   - `<nav>`、`<header>`、`<menu>`要素内のリンクを収集
   - 相対パスを絶対URLに変換
   - JavaScriptリンクやフラグメントを除外

2. サイトマップからのURL収集
   - `robots.txt`からサイトマップURLを取得
   - XMLの名前空間を考慮したパース処理
   - 複数のサイトマップに対応

3. エラーハンドリング
   - ネットワークエラーの適切な処理
   - レート制限への対応
   - タイムアウト処理

#### 使用例

```python
from app.crawlers.url_collector import URLCollector

collector = URLCollector(
    max_concurrent_requests=3,  # 同時リクエスト数の制限
    request_timeout=30.0,       # タイムアウト時間（秒）
)

# ナビゲーションメニューからURL収集
nav_urls = await collector.collect_from_navigation('https://example.com')

# サイトマップからURL収集
sitemap_urls = await collector.collect_from_sitemap('https://example.com')
```

### 非同期処理の最適化

1. 同時実行数の制御
   ```python
   # セマフォを使用した制御
   self._semaphore = asyncio.Semaphore(max_concurrent_requests)
   
   async with self._semaphore:
       # リクエスト処理
   ```

2. セッション管理
   ```python
   async with aiohttp.ClientSession(headers=headers) as session:
       # 複数のリクエストで同じセッションを再利用
   ```

3. タイムアウト設定
   ```python
   timeout = aiohttp.ClientTimeout(total=30.0)
   session = aiohttp.ClientSession(timeout=timeout)
   ```

### エラーハンドリング

1. ネットワークエラー
   ```python
   try:
       async with session.get(url) as response:
           if response.status >= 400:
               raise NetworkError(f"ステータスコード {response.status}")
   except aiohttp.ClientError as e:
       raise NetworkError(f"ネットワークエラー: {str(e)}")
   ```

2. レート制限
   ```python
   if response.status == 429:
       raise RateLimitError("レート制限に達しました")
   ```

3. タイムアウト
   ```python
   try:
       async with session.get(url, timeout=self.timeout) as response:
           return await response.text()
   except asyncio.TimeoutError:
       raise NetworkError("リクエストがタイムアウトしました")
   ```

## 開発環境の構築

1. 開発用の依存パッケージをインストール
```bash
make install
```

2. pre-commitフックを設定
```bash
pre-commit install
```

3. テストを実行して動作確認
```bash
make test-all
```

## テストの実装

### 統合テスト

1. テストサーバーの設定
```python
@pytest.fixture
async def test_app():
    app = web.Application()
    app.router.add_get('/', handle_navigation)
    app.router.add_get('/robots.txt', handle_robots)
    return app
```

2. 非同期テストの実装
```python
@pytest.mark.asyncio
async def test_collect_from_navigation(test_client):
    collector = URLCollector()
    urls = await collector.collect_from_navigation(base_url)
    assert len(urls) == expected_count
```

3. エラーケースのテスト
```python
@pytest.mark.asyncio
async def test_error_handling(test_client):
    with pytest.raises(NetworkError):
        await collector.collect_from_navigation(error_url)
```

### テストの実行方法

```bash
# 特定のテストファイルを実行
pytest tests/integration/test_url_collector.py -v

# カバレッジレポート付きで実行
pytest --cov=app --cov-report=term-missing

# デバッグログ付きで実行
pytest -v --log-cli-level=DEBUG
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
