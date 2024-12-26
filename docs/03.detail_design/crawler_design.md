# 詳細設計書

## 1. クローラー実装詳細

### 1.1 BaseCrawler クラス
```python
class BaseCrawler(ABC):
    """
    クローラーの基本クラス
    
    Attributes:
        session (Session): データベースセッション
        headers (Dict[str, str]): HTTPリクエストヘッダー
        timeout (int): リクエストタイムアウト（秒）
        max_retries (int): リトライ回数
        logger (logging.Logger): ロガー
    """
    
    def __init__(self, session: Optional[Session] = None, ...):
        """初期化処理"""
        pass
    
    def _make_request(self, url: str, method: str = 'GET', ...) -> Response:
        """HTTPリクエストの実行"""
        pass
    
    @abstractmethod
    def crawl(self) -> None:
        """クローリングの実行"""
        pass
    
    def save(self, data: Any) -> None:
        """データの保存"""
        pass
```

### 1.2 CompanyCrawler クラス
```python
class CompanyCrawler(BaseCrawler):
    """
    企業情報クローラー
    
    Attributes:
        company_code (str): 企���コード
        base_url (str): 基本URL
    """
    
    def crawl(self) -> None:
        """企業情報のクロール"""
        # 1. 企業情報の取得
        # 2. 財務情報の取得
        # 3. ニュースの取得
        pass
    
    def parse_company(self, response: Response) -> Dict[str, Any]:
        """企業情報のパース"""
        pass
    
    def parse_financial(self, response: Response) -> List[Dict[str, Any]]:
        """財務情報のパース"""
        pass
    
    def parse_news(self, response: Response) -> List[Dict[str, Any]]:
        """ニュース情報のパース"""
        pass
```

## 2. スクレイピング仕様

### 2.1 ニトリホールディングス

#### 2.1.1 企業情報
- URL: https://www.nitorihd.co.jp/company/
- 取得項目：
  ```
  - 社名: .company-name
  - 設立日: .company-info tr:nth-child(3) td
  - 事業内容: .company-info tr:nth-child(5) td
  ```

#### 2.1.2 財務情報
- URL: https://www.nitorihd.co.jp/ir/library/result.html
- 取得項目：
  ```
  - 決算期: .financial-table tr td:nth-child(1)
  - 売上高: .financial-table tr td:nth-child(2)
  - 営業利益: .financial-table tr td:nth-child(3)
  ```

#### 2.1.3 ニュース
- URL: https://www.nitorihd.co.jp/ir/news/
- 取得項目：
  ```
  - 日付: .news-list .date
  - タイトル: .news-list .title
  - リンク: .news-list a
  ```

## 3. データ正規化ルール

### 3.1 企業情報
1. 企業コード
   - 4桁の数値
   - 必須項目

2. 企業名
   - 全角文字
   - 空白を削除
   - 必須項目

3. 設立日
   - YYYY-MM-DD形式
   - 必須項目

### 3.2 財務情報
1. 会計期間
   - "YYYY年度"形式
   - 必須項目

2. 金額
   - 単位：円
   - カンマを削除
   - 数値型に変換

3. 日付
   - YYYY-MM-DD形式
   - タイムゾーン：JST

### 3.3 ニュース
1. 日時
   - YYYY-MM-DD HH:MM:SS形式
   - タイムゾーン：JST

2. タイトル
   - 前後の空白を削除
   - HTML特殊文字をデコード

3. URL
   - 相対パスを絶対パスに変換
   - URLエンコード

## 4. エラー処理詳細

### 4.1 接続エラー
```python
try:
    response = requests.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.Timeout:
    self.logger.error(f"Timeout accessing {url}")
    self._handle_timeout_error()
except requests.HTTPError as e:
    self.logger.error(f"HTTP error {e.response.status_code} for {url}")
    self._handle_http_error(e)
```

### 4.2 パースエラー
```python
try:
    soup = BeautifulSoup(response.text, 'html.parser')
    data = self._extract_data(soup)
    self._validate_data(data)
except ValueError as e:
    self.logger.error(f"Invalid data format: {str(e)}")
    self._handle_parse_error(e)
```

### 4.3 データベースエラー
```python
try:
    self.session.add(model)
    self.session.commit()
except SQLAlchemyError as e:
    self.logger.error(f"Database error: {str(e)}")
    self.session.rollback()
    self._handle_db_error(e)
```

## 5. ログ設計

### 5.1 ログレベル
1. DEBUG
   - リクエスト詳細
   - レスポンス詳細
   - パース処理詳細

2. INFO
   - クロール開始・終了
   - データ保存成功
   - リトライ実行

3. WARNING
   - 一時的なエラー
   - リトライ実行
   - データ不整合

4. ERROR
   - 重大なエラー
   - 処理中断
   - データベースエラー

### 5.2 ログフォーマット
```python
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
```

## 6. テスト計画

### 6.1 単体テスト
1. クローラー基本機能
   - リクエスト処理
   - エラーハンドリング
   - データ保存

2. パース処理
   - 正常系データ
   - 異常系データ
   - エッジケース

### 6.2 統合テスト
1. ク��ールフロー
   - 全体フロー
   - エラー発生時の動作
   - リトライ処理

2. データ整合性
   - モデル間の関連
   - 一意制約
   - 外部キー制約 