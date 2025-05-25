# A2A プロトタイプ 使用方法ガイド

## 🎉 実装完了！

A2A（Agent-to-Agent）プロトコルのプロトタイプ実装が完了しました。実際に動作するエージェントを起動してテストできます。

## 📋 実装済みエージェント

### 1. Weather Agent (天気情報エージェント)
- **URL**: http://localhost:8001
- **機能**: 
  - 現在の天気情報取得
  - 天気予報取得
  - 対応地域: 東京、大阪、名古屋、福岡、札幌、仙台

### 2. Calculator Agent (数学計算エージェント)  
- **URL**: http://localhost:8002
- **機能**:
  - 基本四則演算
  - 高度な数学関数（sin, cos, tan, log, sqrt等）
  - 簡単な方程式解決

## 🚀 エージェント起動方法

### Weather Agent を起動
```bash
cd /home/devuser/workspace
python app/a2a_prototype/scripts/start_weather_agent.py
```

### Calculator Agent を起動
```bash
cd /home/devuser/workspace  
python app/a2a_prototype/scripts/start_calculator_agent.py
```

## ✅ 起動確認

正常に起動すると以下のようなログが表示されます：

```
==================================================
🌤️  Weather Agent Starting...
==================================================
Agent URL: http://localhost:8001
Agent Card available at: http://localhost:8001/.well-known/agent.json

エージェントが起動しました。停止するには Ctrl+C を押してください。

Starting A2A server on http://localhost:8001/a2a
Google A2A compatibility: Enabled
 * Running on http://localhost:8001
```

## 🔍 エージェントカード確認

エージェントが起動したら、ブラウザまたはcurlでエージェントカードを確認できます：

```bash
# Weather Agent のエージェントカード
curl http://localhost:8001/.well-known/agent.json

# Calculator Agent のエージェントカード  
curl http://localhost:8002/.well-known/agent.json
```

## 🧪 テストクライアント使用方法

対話式テストクライアントでエージェントと通信できます：

```bash
cd /home/devuser/workspace
python app/a2a_prototype/clients/test_client.py
```

### テストコマンド例

```bash
# エージェントのヘルスチェック
A2A> test weather

# メッセージ送信テスト
A2A> send weather 東京の天気を教えて
A2A> send calculator 5 + 3 を計算して

# 終了
A2A> quit
```

### コマンドライン引数での簡単テスト

```bash
# Weather Agent テスト
python app/a2a_prototype/clients/test_client.py weather-test

# Calculator Agent テスト
python app/a2a_prototype/clients/test_client.py calculator-test
```

## 🛠️ 技術スタック

- **A2Aライブラリ**: python-a2a
- **Webフレームワーク**: Flask (python-a2a内蔵)
- **プロトコル**: A2A Protocol v1.0 + JSON-RPC 2.0
- **互換性**: Google A2A Protocol準拠

## 📁 ファイル構成

```
app/a2a_prototype/
├── agents/              # エージェント実装
│   ├── base_agent.py    # 基底クラス
│   ├── weather_agent.py # 天気エージェント
│   └── calculator_agent.py # 計算エージェント
├── scripts/             # 起動スクリプト
├── clients/             # テストクライアント
└── utils/               # 設定・ユーティリティ
```

## 🎯 次のステップ

1. **エージェント間通信**: 2つのエージェント間でのA2A通信実装
2. **Orchestrator Agent**: 複数エージェントを調整するエージェント
3. **実用デモ**: 旅行計画等の現実的なユースケース
4. **本格運用**: エラーハンドリング、認証、ログ機能

## 🐛 トラブルシューティング

### ポート競合エラー
```bash
# ポートを使用しているプロセスを確認
lsof -i :8001
lsof -i :8002

# プロセス終了
kill <PID>
```

### 依存関係エラー
```bash
# 依存関係を再インストール
poetry install
```

### インポートエラー
- PYTHONPATHが正しく設定されているか確認
- 作業ディレクトリが `/home/devuser/workspace` であることを確認

## 📝 ログの場所

エージェントのログはコンソールに出力されます。デバッグ用のINFOレベルログが表示されます。

---

🎉 **おめでとうございます！** A2Aプロトタイプが動作しています。実際にエージェント同士が通信する世界をお楽しみください！ 