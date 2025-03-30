# API連携 実装例

`techContext.md` (旧版) より抽出した外部API連携に関する実装例や設定例。

## Dify API連携例

### 設定項目
*   **エンドポイントホスト:** 環境変数 `DIFY_HOST` または `QueryMonitor` 初期化パラメータで設定 (デフォルト: `http://localhost:5001`)。
*   **APIキー:** 環境変数 `DIFY_API_KEY` で設定。
*   **エンドポイントパス (例):** `/v1/chat-messages` (旧: `/v1/completion-messages`)
*   **認証:** `Authorization: Bearer [APIキー]` ヘッダー。
*   **レスポンスモード (例):** `blocking` / `streaming`。

### リクエスト例 (`aiohttp`)
```python
import aiohttp

async def call_dify(session: aiohttp.ClientSession, host: str, api_key: str, query: str):
    url = f"{host}/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "", # 必要に応じて設定
        "user": "my-app" # 識別子
    }
    # タイムアウトは session 作成時に設定 (下記 aiohttp 設定例参照)
    async with session.post(url, headers=headers, json=payload) as response:
        response.raise_for_status() # ステータスコードチェック
        return await response.json()
```

## Slack API連携例 (`slack_sdk`)

### 設定項目
*   **トークン:** 環境変数 `SLACK_TOKEN` で設定。
*   **利用クライアント:** `slack_sdk.web.async_client.AsyncWebClient`

### 通知例
```python
from slack_sdk.web.async_client import AsyncWebClient

async def send_slack_message(client: AsyncWebClient, channel: str, text: str, blocks: list):
    await client.chat_postMessage(
        channel=channel,
        text=text, # フォールバック用テキスト
        blocks=blocks # Block Kit UI
    )

# Block Kit 例 (成功時)
success_blocks = [
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "✅ 処理成功"},
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "処理結果の詳細..."},
    },
]

# Block Kit 例 (エラー時)
error_blocks = [
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "❌ エラー発生"},
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "エラー内容の詳細..."},
    },
]
```

### エラーハンドリング
*   `slack_sdk.errors.SlackApiError` を捕捉して対応。

## 非同期HTTPクライアント (`aiohttp`)

### セッション設定例
```python
import aiohttp
import asyncio

# タイムアウト設定 (例: 60秒)
# Difyのような長時間応答する可能性のあるAPIでは、より長いタイムアウトが必要な場合がある (例: 360秒)
timeout_seconds = 60
timeout = aiohttp.ClientTimeout(total=timeout_seconds)

# コネクタ設定 (例: SSL検証無効 - 開発環境向け)
# connector = aiohttp.TCPConnector(ssl=False)
connector = aiohttp.TCPConnector()

# セッション作成
session = aiohttp.ClientSession(timeout=timeout, connector=connector)

# 利用後、セッションをクローズすること
# await session.close()
# または async with aiohttp.ClientSession(...) を使用する
```

### リトライ実装の考慮
*   `aiohttp` 自体には高度なリトライ機能は組み込まれていないため、`tenacity` ライブラリなどを使用するか、自前で指数バックオフなどのリトライロジックを実装する必要がある。

## 依存関係（例）

*   aiohttp>=3.8.0
*   slack-sdk>=3.0.0

**(注意: 上記バージョンは旧 `techContext.md` に記載されていた例であり、実際のプロジェクトに合わせて更新が必要です)** 