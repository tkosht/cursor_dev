# 運用関連パターン

`techContext.md` (旧版) より抽出したタイムアウト、リトライ、ロギング、デプロイメント等に関するパターンや設定例。

## タイムアウト設定

### HTTPリクエストタイムアウト (`aiohttp`)
*   **設定方法:** `aiohttp.ClientTimeout(total=秒数)` を `aiohttp.ClientSession` 作成時に渡す。
*   **設定例:** `timeout = aiohttp.ClientTimeout(total=60)` (60秒)
*   **考慮事項:** 連携先APIの応答時間に応じて適切な値を設定する。長時間かかる可能性のあるAPI (例: Dify) では、長めのタイムアウト (例: 360秒) が必要になる場合がある。
*   **環境変数での管理:** `REQUEST_TIMEOUT` のような環境変数で設定値を管理し、デプロイ環境ごとに調整可能にするのが望ましい。

## リトライ処理

### HTTPリクエストリトライ
*   **考え方:** 一時的なネットワークエラーやサーバー側の問題に備え、リトライ処理を実装する。
*   **実装方法:**
    *   ライブラリ利用: `tenacity` などのリトライ用ライブラリを利用する。
    *   手動実装: 指数バックオフ（Exponential Backoff）などのアルゴリズムで、リトライ間隔を徐々に長くしながら再試行する。
*   **設定例 (概念):**
    *   最大リトライ回数: 3回
    *   リトライ間隔: 指数バックオフ (例: 1秒, 2秒, 4秒...)
    *   リトライ対象: 接続エラー、タイムアウト、特定ステータスコード (例: 5xx系) など。

## ロギング

### 設定例 (`logging` モジュール)
*   **ログレベル:** `INFO`, `WARNING`, `ERROR`, `DEBUG` など、状況に応じて設定。
*   **出力先:** ファイル (`logging.FileHandler`, `logging.handlers.RotatingFileHandler`) や標準出力 (`logging.StreamHandler`)。
*   **フォーマット:** 日時、ログレベル、モジュール名、メッセージなどを含むように設定 (`logging.Formatter`)。
*   **ローテーション:** ログファイルが肥大化しないように、サイズや日付でローテーションする (`logging.handlers.RotatingFileHandler`, `logging.handlers.TimedRotatingFileHandler`)。

```python
import logging
import logging.handlers

# ロガー設定例
logger = logging.getLogger('my_app_logger')
logger.setLevel(logging.INFO) # ログレベル設定

# フォーマッター
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ファイルハンドラー (例: 10MBでローテーション、5世代保持)
# log_file = 'app.log'
# file_handler = logging.handlers.RotatingFileHandler(
#     log_file, maxBytes=10*1024*1024, backupCount=5
# )
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# コンソールハンドラー
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 使用例
logger.info("処理開始")
try:
    # ... 処理 ...
    logger.info("処理成功")
except Exception as e:
    logger.error(f"エラー発生: {e}", exc_info=True) # トレースバックも記録
```

### ログ設計の考慮事項
*   **ログレベル:** 本番環境では `INFO` 以上、開発中は `DEBUG` など、環境に応じて切り替える。
*   **情報量:** エラー発生時には原因特定に必要な情報（トレースバック、関連パラメータなど）を含める。
*   **機密情報:** ログにパスワードやAPIキーなどの機密情報を含めないように注意する（マスキングなど）。

## デプロイメント・監視 (例)

*   **実行環境:**
    *   cron などOSのスケジューラによる定期実行。
    *   Dockerコンテナ環境。
*   **監視:**
    *   ログファイルの監視（エラー発生時に通知など）。
    *   プロセスの死活監視。
    *   外部サービスの監視ツール連携 (例: Datadog, Sentry)。
*   **ログ管理:**
    *   ログディレクトリのパーミッション管理。
    *   ログの集約・分析基盤 (例: Elasticsearch, Fluentd, Kibana)。 