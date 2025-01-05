# Adoptive Market Crawler

市場分析のための情報収集とナレッジ化システム。指定されたキーワードに関する市場分析に役立つ情報を収集し、Gemini-2.0を用いて解析し、Neo4jデータベースにナレッジとして保存します。

## 機能

- HTMLからの本文抽出と不要要素の除去
- Gemini-2.0-flash-expを使用した市場影響度分析
- Neo4jへのナレッジ保存と時系列管理

## 必要条件

- Python 3.10以上
- Poetry
- Neo4jデータベース
- Google Cloud Platformアカウント（Gemini APIキー用）

## セットアップ

1. リポジトリのクローン:
```bash
git clone [repository-url]
cd adoptive-market-crawler
```

2. 依存関係のインストール:
```bash
poetry install
```

3. 環境変数の設定:
`.env`ファイルを作成し、以下の変数を設定:
```
GOOGLE_API_KEY_GEMINI=your_gemini_api_key
neo4j_user=your_neo4j_username
neo4j_pswd=your_neo4j_password
```

## 使用方法

1. 仮想環境の有効化:
```bash
poetry shell
```

2. テストの実行:
```bash
pytest
```

3. コードフォーマットとリント:
```bash
black app tests
flake8 app tests
```

## プロジェクト構造

```
.
├── app/
│   ├── content_fetcher.py
│   ├── content_parser.py
│   ├── gemini_analyzer.py
│   ├── market_analyzer.py
│   ├── neo4j_manager.py
│   └── knowledge_repository.py
├── tests/
│   └── test_*.py
├── docs/
│   ├── 01.requirements/
│   ├── 02.basic_design/
│   ├── 03.detail_design/
│   └── ...
└── pyproject.toml
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
