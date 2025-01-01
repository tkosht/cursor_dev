# ExtractionManager 詳細設計

## 1. 概要
Webページからの情報抽出を管理するコンポーネント。

## 2. 主要機能

### 2.1 データ抽出
- ページ取得
- HTML解析
- データ抽出
- 検証スコア計算

### 2.2 企業情報抽出
- 基本情報抽出（企業名、事業内容、設立日等）
- 財務情報抽出（売上高、営業利益、純利益等）
- データ形式の正規化
- 抽出精度の検証

## 3. クラス設計

```python
class ExtractionManager:
    async def extract(
        self,
        url: str,
        target_data: Dict[str, Any]
    ) -> ExtractedData:
        """データを抽出"""
        pass

    async def extract_company_info(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """企業情報を抽出"""
        pass

    async def extract_financial_info(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """財務情報を抽出"""
        pass

    def calculate_validation_score(
        self,
        extracted_data: Dict[str, Any],
        expected_schema: Dict[str, Any]
    ) -> float:
        """検証スコアを計算"""
        pass
```

## 4. データ構造

### 4.1 企業情報
```python
class CompanyInfo:
    company_code: str
    name: str
    description: str
    established_date: Optional[date]
    stock_exchange: str
    industry: str
```

### 4.2 財務情報
```python
class FinancialInfo:
    fiscal_year: str
    period_type: str
    period_end_date: date
    revenue: float
    operating_income: float
    net_income: float
```

## 5. 検証ルール

### 5.1 企業情報検証
- 必須項目の存在確認
- データ形式の妥当性確認
- 値の範囲チェック

### 5.2 財務情報検証
- 数値の妥当性確認
- 時系列データの整合性確認
- 異常値の検出

## 6. エラー処理
- 抽出エラーの分類
- リトライ戦略
- エラーログの出力

## 7. パフォーマンス
- 同時実行数の制御
- タイムアウト設定
- キャッシュ戦略 