# アダプティブクローラーの基本設計

## 1. システム構成

### 1.1 主要コンポーネント
- SiteAnalyzer: サイト構造の解析
- LLMManager: LLMとの連携
- CrawlerMonitor: クロール状態の監視

### 1.2 クラス構成
```python
class SiteAnalyzer:
    def __init__(self, llm_manager: LLMManager)
    async def analyze_site_structure(self, base_url: str) -> Dict[str, Any]
    async def _get_sitemap_urls(self, base_url: str) -> List[str]
    async def _get_sitemap_from_robots(self, base_url: str) -> List[str]
    async def _analyze_navigation(self, base_url: str) -> Dict[str, List[str]]
    async def _identify_relevant_pages(self, base_url: str, urls: List[str]) -> List[Dict[str, Any]]
```

## 2. 処理フロー

### 2.1 サイト解析フロー
1. サイトマップの取得
   - robots.txtの確認
   - サイトマップの解析
   - エラー時は代替手段を試行

2. ナビゲーション構造の解析
   - メインナビゲーション
   - フッターナビゲーション
   - その他のナビゲーション要素

3. 関連ページの特定
   - URLのフィルタリング
   - コンテンツの評価
   - スコアリング

### 2.2 エラーハンドリングフロー
1. robots.txt取得エラー
   - エラーをログ出力
   - 処理をスキップ
   - 代替手段を試行
   - 結果を空リストで返却

2. サイトマップ取得エラー
   - エラーをログ出力
   - 一般的な場所を確認
   - 代替手段を試行

3. ページアクセスエラー
   - リトライ処理
   - タイムアウト設定
   - エラー情報の記録

## 3. データ構造

### 3.1 サイト解析結果
```python
{
    "sitemap": List[str],  # サイトマップから取得したURL
    "navigation": {
        "main_nav": List[str],
        "footer_nav": List[str],
        "other_nav": List[str]
    },
    "relevant_pages": List[Dict[str, Any]]  # 関連ページ情報
}
```

### 3.2 ページ情報
```python
{
    "url": str,
    "relevance_score": float,
    "page_type": str,
    "content": Optional[Dict[str, Any]]
}
```

## 4. エラー処理

### 4.1 エラー種別
- HTTPエラー
  - 404: Not Found
  - 403: Forbidden
  - 429: Too Many Requests
  - 500: Internal Server Error
- ネットワークエラー
  - タイムアウト
  - 接続エラー
  - DNS解決エラー
- パースエラー
  - HTML解析エラー
  - XML解析エラー
  - JSON解析エラー

### 4.2 リトライ戦略
- 最大リトライ回数: 3回
- バックオフ時間: 2^n秒
- リトライ対象エラー:
  - 429: Too Many Requests
  - 500: Internal Server Error
  - タイムアウト
  - 一時的な接続エラー

## 5. テスト設計

### 5.1 テストケース
1. アクセンチュア（日本）サイト
   - robots.txt取得
   - サイトマップ解析
   - ナビゲーション構造解析
   - 企業情報ページ特定

2. エラーケース
   - robots.txt取得失敗
   - サイトマップ取得失敗
   - ページアクセス失敗
   - パース失敗

### 5.2 テスト環境
- Python 3.10以上
- aiohttp
- pytest
- pytest-asyncio

## 6. 監視設計

### 6.1 ログ出力
- ログレベル
  - ERROR: エラー発生時
  - INFO: 重要な処理の開始・完了
  - DEBUG: 詳細な処理状況

### 6.2 メトリクス
- 処理時間
- 成功率
- エラー発生率
- リソース使用量 