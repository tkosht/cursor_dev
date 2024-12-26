# 基本設計書

## 1. システム構成

### 1.1 全体構成
```
[Crawler System]
    |
    |-- [Crawler Module]
    |     |-- Base Crawler
    |     |-- Company Crawler
    |     `-- News Crawler
    |
    |-- [Database]
    |     |-- Companies
    |     |-- Financial Data
    |     `-- News
    |
    |-- [Error Handler]
    |     |-- Retry Logic
    |     |-- Error Logger
    |     `-- Notification
    |
    `-- [Monitor]
          |-- Performance Metrics
          |-- Status Check
          `-- Alert System
```

### 1.2 モジュール構成
1. クローラーモジュール
   - 基本クローラー：共通機能の提供
   - 企業クローラー：企業情報の取得
   - ニュースクローラー：ニュース情報の取得

2. データベースモジュール
   - モデル定義
   - データアクセス層
   - マイグレーション管理

3. エラーハンドリングモジュール
   - エラー検出
   - リトライ処理
   - ログ管理

4. 監視モジュール
   - メトリクス収集
   - ステータス管理
   - アラート通知

## 2. クローラー設計

### 2.1 基本クローラー
1. 機能
   - HTTPリクエスト処理
   - レスポンス解析
   - エラーハンドリング
   - セッション管理

2. インターフェース
   - 初期化処理
   - クロール実行
   - データ保存
   - エラー通知

### 2.2 企業クローラー
1. 機能
   - 企業情報の取得
   - 財務情報の取得
   - データの正規化
   - 保存処理

2. 処理フロー
   ```
   1. 企業ページへアクセス
   2. 基本情報の抽出
   3. 財務情報の抽出
   4. データの検証
   5. データベースへの保存
   ```

### 2.3 ニュースクローラー
1. 機能
   - ニュース一覧の取得
   - 詳細情報の取得
   - 更新情報の確認
   - 重複チェック

2. 処理フロー
   ```
   1. ニュース一覧ページへアクセス
   2. 新着ニュースの検出
   3. 詳細情報の取得
   4. コンテンツの解析
   5. データベースへの保存
   ```

## 3. データモデル設計

### 3.1 企業テーブル
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    company_code TEXT NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    description TEXT,
    established_date DATE,
    website_url TEXT,
    stock_exchange TEXT,
    industry TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 3.2 財務テーブル
```sql
CREATE TABLE financials (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    fiscal_year TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period_end_date DATE,
    revenue BIGINT,
    operating_income BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

### 3.3 ニューステーブル
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    published_at TIMESTAMP,
    source TEXT,
    category TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

## 4. エラーハンドリング設計

### 4.1 エラー種別
1. 接続エラー
   - タイムアウト
   - DNS解決エラー
   - SSL証明書エラー

2. データエラー
   - パース失敗
   - データ不整合
   - バリデーションエラー

3. システムエラー
   - メモリ不足
   - ディスク容量不足
   - データベースエラー

### 4.2 リトライ戦略
1. 基本方針
   - 最大リトライ回数：3回
   - リトライ間隔：指数バックオフ
   - タイムアウト：30秒

2. エラー別対応
   - 一時的なエラ��：リトライ
   - 永続的なエラー：即時エラー
   - データエラー：ログ記録

## 5. 監視設計

### 5.1 メトリクス
1. パフォーマンス
   - レスポンス時間
   - クロール成功率
   - データ取得量

2. リソース
   - CPU使用率
   - メモリ使用量
   - ディスク使用量

### 5.2 アラート
1. 重要度
   - 緊急：即時対応必要
   - 警告：24時間以内に対応
   - 情報：定期確認

2. 通知方法
   - ログ記録
   - エラーファイル出力
   - メール通知（将来対応） 