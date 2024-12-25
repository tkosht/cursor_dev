# ニトリホールディングス情報クローラー

## 概要
このプロジェクトは、ニトリホールディングスの企業情報や決算情報を自動的に収集するWebクローラーです。

## 機能
- 企業の基本情報の取得
- 決算情報のPDFダウンロードと解析
- 動的HTMLコンテンツのクロール
- データの構造化と保存

## セットアップ
1. 必要な依存関係のインストール
```bash
poetry install
```

2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

3. Playwrightのブラウザインストール
```bash
poetry run playwright install chromium
```

## 使用方法
```bash
# クローラーの実行
poetry run python -m app.crawler.main

# テストの実行
poetry run pytest
```

## 開発環境
- Python 3.10+
- Poetry
- Playwright
- Beautiful Soup 4

## ライセンス
MIT License
