import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ログディレクトリの作成
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # コンソール出力
        logging.StreamHandler(),
        # ファイル出力（ローテーション）
        RotatingFileHandler(
            os.path.join(log_dir, "query_monitor.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger(__name__)


class QueryExecutionError(Exception):
    """クエリ実行時のエラーを表すカスタム例外"""
    pass


class SlackNotificationError(Exception):
    """Slack通知時のエラーを表すカスタム例外"""
    pass


class QueryMonitor:
    """クエリ実行とSlack通知を管理するクラス"""

    def __init__(
        self,
        dify_api_key: str,
        slack_token: str,
        slack_channel: str,
        slack_client: Optional[WebClient] = None,
        session: Optional[requests.Session] = None
    ) -> None:
        """
        初期化

        Args:
            dify_api_key (str): Dify APIキー
            slack_token (str): Slackトークン
            slack_channel (str): Slackチャンネル
            slack_client (Optional[WebClient], optional): Slackクライアント. Defaults to None.
            session (Optional[requests.Session], optional): セッション. Defaults to None.

        Raises:
            ValueError: 必要なパラメータが不足している場合
        """
        if not all([dify_api_key, slack_token, slack_channel]):
            raise ValueError("All parameters are required")

        self.dify_api_key = dify_api_key
        self.slack_channel = slack_channel
        self.slack_client = slack_client or WebClient(token=slack_token)
        self.session = session or requests.Session()

        # リトライ設定
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        # クエリ設定の読み込み
        self._load_queries()

    def _load_queries(self) -> None:
        """
        queries.jsonからクエリ設定を読み込む

        Raises:
            FileNotFoundError: クエリ設定ファイルが見つからない場合
            json.JSONDecodeError: JSONの解析に失敗した場合
        """
        try:
            with open("app/queries.json", "r", encoding="utf-8") as f:
                self.queries = json.load(f)["queries"]
        except FileNotFoundError:
            logger.error("queries.json not found")
            raise
        except json.JSONDecodeError as e:
            logger.error("Failed to parse queries.json: %s", e)
            raise

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Dify APIを使用してクエリを実行

        Args:
            query: 実行するクエリ文字列

        Returns:
            Dict[str, Any]: クエリ実行結果

        Raises:
            QueryExecutionError: クエリ実行に失敗した場合
        """
        try:
            start_time = time.time()
            response = await self.session.post(
                "https://api.dify.ai/v1/completion-messages",
                headers={
                    "Authorization": f"Bearer {self.dify_api_key}",
                    "Content-Type": "application/json"
                },
                json={"query": query},
                timeout=30
            )
            response.raise_for_status()
            execution_time = time.time() - start_time
            logger.info("Query executed successfully in %.2f seconds", execution_time)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Query execution failed: %s", e)
            await self._send_error_notification("クエリ実行エラー", str(e))
            raise QueryExecutionError(f"Failed to execute query: {e}")

    async def _send_error_notification(self, title: str, error_message: str) -> None:
        """
        エラー通知をSlackに送信

        Args:
            title: エラーのタイトル
            error_message: エラーメッセージ
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"⚠️ {title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{error_message}```"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"発生時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]

            await self.slack_client.chat_postMessage(
                channel="errors",
                text=f"エラー: {title}",
                blocks=blocks
            )
            logger.info("Error notification sent: %s", title)
        except SlackApiError as e:
            logger.error("Failed to send error notification: %s", e.response["error"])

    async def send_slack_notification(
        self, channel: str, message: str, status: str = "info"
    ) -> None:
        """
        クエリ結果をSlackに通知

        Args:
            channel: 通知先のSlackチャンネル
            message: 通知メッセージ
            status: 通知の状態（success, warning, error, info）

        Raises:
            SlackNotificationError: Slack通知に失敗した場合
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "クエリ実行結果"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"ステータス: {status}"
                        }
                    ]
                },
                {"type": "divider"}
            ]

            await self.slack_client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text=message
            )

        except SlackApiError as e:
            logger.error("Failed to send Slack notification: %s", e.response["error"])
            raise SlackNotificationError(f"Failed to send notification: {e.response['error']}")

    async def process_query(self, query: str, channel: str) -> None:
        """クエリを実行し、結果をSlackに通知する"""
        try:
            # クエリを実行
            result = await self.execute_query(query)

            # 結果の検証
            if not result.get("answer"):
                await self.send_slack_notification(
                    channel,
                    "結果が空です",
                    "warning"
                )
                return

            # 結果をSlackに通知
            await self.send_slack_notification(
                channel,
                result["answer"],
                "success"
            )

        except requests.exceptions.Timeout:
            await self.send_slack_notification(
                channel,
                "タイムアウトが発生しました",
                "error"
            )
        except requests.exceptions.ConnectionError:
            await self.send_slack_notification(
                channel,
                "接続エラーが発生しました",
                "error"
            )
        except requests.exceptions.HTTPError as e:
            await self.send_slack_notification(
                channel,
                f"HTTPエラーが発生しました: {str(e)}",
                "error"
            )
        except ValueError:
            await self.send_slack_notification(
                channel,
                "JSONの解析に失敗しました",
                "error"
            )
        except Exception as e:
            await self.send_slack_notification(
                channel,
                f"予期せぬエラーが発生しました: {str(e)}",
                "error"
            )


async def main() -> None:
    """
    メイン実行関数
    """
    try:
        # 環境変数の検証
        dify_api_key = os.getenv("DIFY_API_KEY")
        slack_token = os.getenv("SLACK_TOKEN")
        slack_channel = os.getenv("SLACK_CHANNEL")

        if not all([dify_api_key, slack_token, slack_channel]):
            raise ValueError("Required environment variables are not set")

        # モニターの初期化
        monitor = QueryMonitor(dify_api_key, slack_token, slack_channel)

        # 全クエリの実行
        for query in monitor.queries:
            await monitor.process_query(query["query"], query["channel"])

    except Exception as e:
        logger.error("Application error: %s", e)
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
