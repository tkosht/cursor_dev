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

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
