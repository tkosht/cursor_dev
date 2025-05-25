# cursor_dev - A2A Protocol Research & Implementation

A2A（Agent-to-Agent）プロトコルの研究・実装プロジェクトです。エージェント間連携システムのプロトタイプを通じて、実用的なA2A技術の習得と検証を行います。

## 🎯 プロジェクト概要

### 現在の実装状況
- **✅ A2Aプロトタイプ実装完了**: 動作するエージェント実装済み
- **✅ 技術調査完了**: A2Aプロトコル詳細調査・評価完了
- **✅ コード品質確保**: Linter・型チェック完了

### 実装済みエージェント
1. **Weather Agent** (http://localhost:8001)
   - 天気情報提供エージェント
   - 対応地域: 東京、大阪、名古屋、福岡、札幌、仙台

2. **Calculator Agent** (http://localhost:8002)  
   - 数学計算エージェント
   - 基本四則演算、高度な数学関数、方程式解決

## 🚀 クイックスタート

### 必要な環境
- Python 3.10+
- Poetry
- VSCode Dev Container（推奨）

### エージェント起動

```bash
# Weather Agent を起動
python app/a2a_prototype/scripts/start_weather_agent.py

# Calculator Agent を起動  
python app/a2a_prototype/scripts/start_calculator_agent.py
```

### テスト実行

```bash
# 対話式テストクライアント
python app/a2a_prototype/clients/test_client.py

# 個別テスト
python app/a2a_prototype/clients/test_client.py weather-test
python app/a2a_prototype/clients/test_client.py calculator-test
```

## 📋 技術スタック

- **A2Aライブラリ**: python-a2a
- **Webフレームワーク**: Flask (python-a2a内蔵)
- **プロトコル**: A2A Protocol v1.0 + JSON-RPC 2.0
- **互換性**: Google A2A Protocol準拠
- **開発環境**: VSCode Dev Container
- **依存管理**: Poetry

## 📁 プロジェクト構造

```
cursor_dev/
├── app/a2a_prototype/          # A2Aプロトタイプ実装
│   ├── agents/                 # エージェント実装
│   │   ├── base_agent.py       # 基底クラス
│   │   ├── weather_agent.py    # 天気エージェント
│   │   └── calculator_agent.py # 計算エージェント
│   ├── scripts/                # 起動スクリプト
│   ├── clients/                # テストクライアント
│   └── utils/                  # 設定・ユーティリティ
├── memory-bank/                # AIの記憶領域
├── docs/                       # プロジェクトドキュメント
├── .devcontainer/              # Dev Container設定
└── A2A_PROTOTYPE_USAGE.md      # 詳細な使用方法
```

## 📖 ドキュメント

### 基本ドキュメント
- **[A2A_PROTOTYPE_USAGE.md](A2A_PROTOTYPE_USAGE.md)**: 詳細な使用方法ガイド
- **[memory-bank/projectbrief.md](memory-bank/projectbrief.md)**: プロジェクト概要
- **[memory-bank/progress.md](memory-bank/progress.md)**: 現在の進捗状況

### 技術調査資料
- **[memory-bank/research/](memory-bank/research/)**: A2Aプロトコル調査結果
- **[memory-bank/a2a_implementation_plan.md](memory-bank/a2a_implementation_plan.md)**: 実装計画書

## 🧪 開発・テスト

### コード品質チェック

```bash
# linterチェック
flake8 app/

# 型チェック  
mypy app/ --ignore-missing-imports

# フォーマット
black app/
```

### 依存関係管理

```bash
# 環境構築
poetry install

# 依存関係追加
poetry add <package>
```

## 🎯 次のステップ

1. **エージェント間通信**: 実際のA2A通信プロトコルでの連携実装
2. **Orchestrator Agent**: 複数エージェント調整エージェント
3. **実用デモシナリオ**: 旅行計画等の現実的なユースケース
4. **本格運用準備**: エラーハンドリング、認証、監視機能

## 🤝 開発プロセス

このプロジェクトでは、Memory Bank駆動の開発プロセスを採用しています：

1. **調査・計画**: memory-bank/に知識・計画を蓄積
2. **実装**: 段階的な実装とテスト
3. **文書化**: 実装結果をmemory-bankに反映
4. **品質管理**: linter・テストによる品質確保

---

**🎉 A2Aプロトタイプが動作中です！** 実際にエージェント同士が通信する世界をお楽しみください。
