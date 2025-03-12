import asyncio
import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

import aiohttp
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ログディレクトリの作成
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # コンソール出力
        logging.StreamHandler(),
        # ファイル出力（ローテーション）
        RotatingFileHandler(
            os.path.join(log_dir, "query_monitor.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)


def load_environment() -> None:
    """環境変数を読み込む"""
    load_dotenv()


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
        dify_host: Optional[str] = None,
        slack_client: Optional[WebClient] = None,
        session: Optional[aiohttp.ClientSession] = None,
        request_timeout: int = 60,
    ) -> None:
        """
        QueryMonitorの初期化

        Args:
            dify_api_key (str): Dify APIキー
            slack_token (str): Slack APIトークン
            slack_channel (str): Slack通知先チャンネル
            dify_host (Optional[str], optional): Dify APIホスト. Defaults to None.
            slack_client (Optional[WebClient], optional): Slackクライアント. Defaults to None.
            session (Optional[aiohttp.ClientSession], optional): aiohttpセッション. Defaults to None.
            request_timeout (int, optional): リクエストのタイムアウト秒数. Defaults to 60.

        Raises:
            ValueError: 必要なパラメータが不足している場合
        """
        if not all([dify_api_key, slack_token, slack_channel]):
            raise ValueError("All parameters are required")
        
        self.dify_api_key = dify_api_key
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.dify_host = dify_host or os.getenv("DIFY_HOST", "http://localhost:5001")
        self.slack_client = slack_client or WebClient(token=slack_token)
        self.request_timeout = request_timeout
        
        self._session = session or aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        self.queries = []
        
        logger.info("Using Dify API endpoint: %s", self.dify_host)

        # クエリ設定の読み込み
        self._load_queries()

    @property
    def session(self) -> aiohttp.ClientSession:
        """セッションを取得"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            connector = aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300,
                force_close=True,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self._session

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリーポイント"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了処理"""
        if self._session:
            await self._session.close()
            self._session = None

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

    async def execute_query(self, query: str, response_mode: str = "blocking") -> Dict[str, Any]:
        """
        Dify APIを使用してクエリを実行

        Args:
            query: 実行するクエリ文字列
            response_mode: レスポンスモード ("blocking" または "streaming")

        Returns:
            Dict[str, Any]: クエリ実行結果

        Raises:
            QueryExecutionError: クエリ実行に失敗した場合
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                start_time = time.time()
                timeout = aiohttp.ClientTimeout(total=self.request_timeout)
                async with self.session.post(
                    f"{self.dify_host}/v1/chat-messages",
                    headers={
                        "Authorization": f"Bearer {self.dify_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": {},
                        "query": query,
                        "response_mode": response_mode,
                        "conversation_id": "",
                        "user": "query_monitor"
                    },
                    timeout=timeout,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("Query execution failed: %s, %s", response.status, error_text)
                        raise QueryExecutionError(f"Failed to execute query: {response.status}, {error_text}")
                    
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError as e:
                        error_text = await response.text()
                        logger.error("Failed to parse JSON response: %s, %s", e, error_text)
                        raise QueryExecutionError("Failed to execute query: 200, invalid json")
                    
                    execution_time = time.time() - start_time
                    logger.info(
                        "Query executed successfully in %.2f seconds",
                        execution_time,
                    )
                    return result
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                if attempt < max_retries - 1:
                    logger.warning("Attempt %d failed: %s, retrying in %d seconds...", attempt + 1, e, retry_delay)
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # 指数バックオフ
                    continue
                logger.error("Query execution failed after %d attempts: %s", max_retries, e)
                raise QueryExecutionError(f"Failed to execute query after {max_retries} attempts: {e}")

    async def _send_error_notification(
        self, title: str, error_message: str
    ) -> None:
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
                    "text": {"type": "plain_text", "text": f"⚠️ {title}"},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{error_message}```",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"発生時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                        }
                    ],
                },
            ]

            self.slack_client.chat_postMessage(
                channel=self.slack_channel, text=f"エラー: {title}", blocks=blocks
            )
            logger.info("Error notification sent: %s", title)
        except SlackApiError as e:
            logger.error(
                "Failed to send error notification: %s", e.response["error"]
            )

    async def process_query(self, query: str, channel: str) -> None:
        """クエリを実行し、結果をSlackに通知する"""
        try:
            # クエリの説明を取得
            query_info = next((q for q in self.queries if q["query"] == query), None)
            title = query_info.get("description", "クエリ実行結果") if query_info else "クエリ実行結果"

            # クエリを実行
            result = await self.execute_query(query)

            # 結果の検証
            if not result.get("answer"):
                await self.send_slack_notification(
                    channel, "結果が空です", "warning", title
                )
                return

            # 結果をSlackに通知
            await self.send_slack_notification(
                channel, result["answer"], "success", title
            )

        except aiohttp.ClientError as e:
            error_msg = f"クライアントエラーが発生しました: {str(e)}"
            await self.send_slack_notification(
                channel, error_msg, "error", title
            )
            raise QueryExecutionError(f"Failed to execute query after 3 attempts: {e}")
        except Exception as e:
            error_msg = f"予期せぬエラーが発生しました: {str(e)}"
            await self.send_slack_notification(
                channel, error_msg, "error", title
            )
            raise

    async def send_slack_notification(
        self, channel: str, message: str, status: str = "info", title: str = "クエリ実行結果"
    ) -> None:
        """
        クエリ結果をSlackに通知

        Args:
            channel: 通知先のSlackチャンネル
            message: 通知メッセージ
            status: 通知の状態（success, warning, error, info）
            title: 通知のタイトル

        Raises:
            SlackNotificationError: Slack通知に失敗した場合
        """
        try:
            if status == "warning":
                title = f"⚠️ 警告: {title}"
            elif status == "error":
                title = f"❌ エラー: {title}"
            elif status == "success":
                title = f"✅ {title}"

            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": title},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": message},
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"ステータス: {status}"}
                    ],
                },
                {"type": "divider"},
            ]

            self.slack_client.chat_postMessage(
                channel=channel, blocks=blocks, text=message
            )

        except SlackApiError as e:
            error = e.response["error"]
            logger.error(
                "Failed to send Slack notification: %s", error
            )
            raise SlackNotificationError(
                f"Failed to send notification: {error}"
            )


def load_config():
    """環境変数の設定を読み込む"""
    load_environment()

    dify_api_key = os.getenv("DIFY_API_KEY")
    slack_token = os.getenv("SLACK_TOKEN")
    dify_host = os.getenv("DIFY_HOST")
    
    # タイムアウト設定を環境変数から読み込む
    timeout_str = os.getenv("REQUEST_TIMEOUT", "60")
    try:
        request_timeout = int(timeout_str)
    except ValueError:
        logger.warning("Invalid REQUEST_TIMEOUT value: %s, using default 60 seconds", timeout_str)
        request_timeout = 60

    if not all([dify_api_key, slack_token]):
        raise ValueError("Required environment variables are not set")

    logger.info("Environment variables loaded successfully")
    logger.info("DIFY_HOST: %s", dify_host)
    logger.info("REQUEST_TIMEOUT: %d seconds", request_timeout)
    
    return dify_api_key, slack_token, dify_host, request_timeout


async def execute_all_queries(monitor):
    """すべてのクエリを実行する"""
    for query in monitor.queries:
        try:
            await monitor.process_query(
                query["query"], query["channel"]
            )
        except (QueryExecutionError, SlackNotificationError) as e:
            logger.error("Query execution error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise


async def main():
    """メイン関数"""
    try:
        # 環境変数の読み込み
        dify_api_key, slack_token, dify_host, request_timeout = load_config()

        # モニターの初期化と実行
        async with QueryMonitor(
            dify_api_key=dify_api_key,
            slack_token=slack_token,
            slack_channel="dummy",  # チャンネルはqueries.jsonから取得
            dify_host=dify_host,
            request_timeout=request_timeout,
        ) as monitor:
            # 全クエリの実行
            await execute_all_queries(monitor)

    except ValueError as e:
        logger.error("Environment error: %s", e)
        raise
    except (QueryExecutionError, SlackNotificationError) as e:
        logger.error("Application error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
