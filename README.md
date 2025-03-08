# クエリ実行 Slack 通知ツール

Dify APIを使用してクエリを実行し、結果をSlackチャンネルに通知するツールです。

## 機能

- Dify APIを使用した自然言語クエリの実行
- 結果のSlackチャンネルへの通知
- 複数クエリの一括実行
- エラー通知の自動送信

## 必要条件

- Python 3.10以上
- Slack APIトークン
- Dify APIキー

## セットアップ

1. 依存関係のインストール:
```bash
poetry install
```

2. 環境変数の設定:
`.env`ファイルを作成し、以下の設定を行います：
```
SLACK_TOKEN=xoxb-your-slack-token
DIFY_API_KEY=your-dify-api-key
```

3. クエリ設定:
`app/queries.json`に実行するクエリを設定します：
```json
{
    "queries": [
        {
            "name": "tech_news",
            "description": "テクノロジー業界のニュース要約",
            "query": "今日のテクノロジー業界における重要なニュースを3つ、簡潔にまとめてください。",
            "channel": "tech-news"
        }
    ]
}
```

4. cron設定:
```bash
# 設定ファイルの全クエリを実行
0 * * * * cd /app && /usr/local/bin/python app/query_monitor.py
```

## 使用方法

1. クエリの追加:
`app/queries.json`に新しいクエリを追加します。

2. 実行:
```bash
python app/query_monitor.py
```

## エラー通知

エラーが発生した場合は、`errors`チャンネルに通知が送信されます。

## ログ

ログは`logs/query_monitor.log`に出力されます。
