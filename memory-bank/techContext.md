# 技術コンテキスト

## 開発環境
1. Python環境
   - Python 3.10以上
   - Poetryによる依存関係管理
   - 仮想環境: /.venv

2. 開発ツール
   - VSCode Dev Container
   - Git
   - pytest

## 主要ライブラリ
1. Slack SDK
   - WebClient
   - エラーハンドリング
   - レート制限対応

2. requests
   - HTTP通信
   - リトライ機能
   - タイムアウト設定

3. logging
   - ログローテーション
   - ログレベル管理
   - ファイル出力

## 設定管理
1. 環境変数
   - SLACK_TOKEN
   - DIFY_API_KEY

2. 設定ファイル
   - queries.json
   - ログ設定

## テスト環境
1. テストフレームワーク
   - pytest
   - unittest.mock
   - MagicMock

2. テストカバレッジ
   - 現在: 80%
   - 目標: 90%以上

## デプロイメント
1. 実行環境
   - cronによる定期実行
   - ログディレクトリ管理

2. 監視
   - ログ監視
   - エラー通知
