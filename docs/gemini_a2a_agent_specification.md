# Gemini A2A Agent 詳細仕様書

## 📋 概要

Google Gemini 2.5 Pro を統合したA2Aエージェント実装の詳細仕様書。
ユーザーからの依頼により開発された高機能なAI対話エージェントです。

## 🎯 開発目的・背景

- **要求**: Gemini を使用したA2Aエージェントのサンプル実装
- **技術検証**: A2A Protocol × Gemini 2.5 Pro の実現可能性確認
- **品質重視**: TDD（Test Driven Development）による高品質実装
- **実用性**: 商用レベルのエラーハンドリング・ユーザビリティ

## 🏗️ 技術仕様

### **基本仕様**
- **AIモデル**: Google Gemini 2.5 Pro
- **プロトコル**: A2A Protocol 完全準拠（JSON-RPC 2.0ベース）
- **実装言語**: Python 3.10+
- **非同期処理**: asyncio による高性能処理
- **起動ポート**: 8004 (http://localhost:8004)

### **会話管理**
- **履歴保持**: 最大20メッセージ（10往復）
- **文脈考慮**: 会話履歴を活用したプロンプト構築
- **履歴管理**: 上限到達時の自動古履歴削除

### **入力制限・バリデーション**
- **最大入力長**: 10,000文字
- **入力サニタイゼーション**: 空文字・過長入力の検証
- **エラーハンドリング**: 適切な日本語エラーメッセージ

## 🛠️ 提供スキル

### **1. intelligent_chat**
- **ID**: `chat`
- **機能**: Gemini 2.5 Proによる高度な対話
- **用途**: 自然言語処理、一般的な質問対応
- **タグ**: `["conversation", "ai", "general"]`

### **2. question_answering**
- **ID**: `qa`
- **機能**: 高度なAI能力による質問応答
- **用途**: 知識ベース検索、研究支援、専門的回答
- **タグ**: `["qa", "knowledge", "research"]`

### **3. help_assistant**
- **ID**: `help`
- **機能**: ヘルプとガイダンス提供
- **用途**: 使用方法説明、トラブルサポート
- **タグ**: `["help", "assistance", "guide"]`

## ⚡ 特別コマンド

### **ヘルプコマンド**
- **入力**: `help`, `?`, `ヘルプ`
- **機能**: 詳細なヘルプメッセージ表示
- **内容**: 使い方、特徴、技術仕様、コマンド一覧

### **履歴クリアコマンド**
- **入力**: `clear`, `クリア`, `リセット`
- **機能**: 会話履歴の完全削除
- **応答**: 確認メッセージ表示

### **ステータスコマンド**
- **入力**: `status`, `ステータス`, `状態`
- **機能**: エージェント詳細状態表示
- **内容**: 
  - エージェント名・URL
  - モデル・温度設定
  - API接続状況
  - 会話履歴数
  - APIキー状態（マスク表示）

## 🔧 実装アーキテクチャ

### **クラス構成**
```python
GeminiA2AAgent (BaseA2AAgent継承)
├── GeminiClient (Gemini API連携)
├── GeminiConfig (設定管理)
├── ConversationContext (会話履歴管理)
└── ErrorHandling (例外処理)
```

### **主要ファイル**
- **`app/a2a_prototype/agents/gemini_agent.py`**: メインエージェント実装
- **`app/a2a_prototype/utils/gemini_client.py`**: Gemini API クライアント
- **`app/a2a_prototype/utils/gemini_config.py`**: 設定管理
- **`scripts/run_gemini_agent.py`**: 実行スクリプト
- **`tests/fixtures/gemini_fixtures.py`**: TDDテスト フィクスチャ

### **設定パラメータ**
```python
# デフォルト設定例
model = "gemini-2.5-pro"
temperature = 0.7
max_tokens = 8192
timeout = 30.0
```

## 🚀 使用方法

### **1. 環境準備**
```bash
# API Key設定（必須）
export GEMINI_API_KEY="your-gemini-api-key"
# または .env ファイルに設定
echo "GEMINI_API_KEY=your-api-key" >> .env
```

### **2. エージェント起動**
```bash
# サーバー起動
python scripts/run_gemini_agent.py

# 起動確認
curl http://localhost:8004/.well-known/agent.json
curl http://localhost:8004/health
```

### **3. 対話例**
```bash
# 基本対話
curl -X POST http://localhost:8004/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "こんにちは、Python開発について質問があります"}'

# ステータス確認
curl -X POST http://localhost:8004/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "status"}'

# 会話履歴クリア
curl -X POST http://localhost:8004/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "clear"}'
```

## 🛡️ エラーハンドリング・セキュリティ

### **エラー分類と対応**
1. **入力バリデーションエラー**
   - 空文字入力 → 「入力が空です」
   - 過長入力 → 「入力が長すぎます（最大10,000文字）」

2. **Gemini APIエラー**
   - 一時的障害 → 「AIサービスに一時的な問題が発生しています」
   - 認証エラー → API設定ガイダンス表示

3. **予期しないエラー**
   - システム例外 → 「予期しない問題が発生しました」
   - 詳細ログ記録 → 管理者向けデバッグ情報

### **セキュリティ配慮**
- **APIキーマスキング**: ログ・ステータス表示でマスク化
- **入力サニタイゼーション**: 悪意ある入力の検証・無害化
- **エラー情報制限**: 内部詳細情報の非表示化

## 📊 品質・パフォーマンス

### **品質指標**
- **TDD実装**: 全機能でテストファースト開発
- **カバレッジ**: 90%以上（プロジェクト全体92.6%）
- **コード品質**: Flake8違反ゼロ、型チェック完了

### **パフォーマンス特性**
- **レスポンス時間**: 通常1-3秒（Gemini API依存）
- **同時接続**: 複数セッション対応
- **メモリ効率**: 会話履歴上限による適切な管理

## ⚠️ 制約・注意事項

### **技術的制約**
- **GEMINI_API_KEY必須**: Google AI Studio でAPIキー取得必要
- **インターネット接続**: Gemini APIアクセスに必要
- **レート制限**: Google Gemini APIの利用制限に従う

### **プライバシー・データ**
- **対話データ**: Googleのサービスを経由（利用規約に従う）
- **ログ記録**: ローカルファイル（gemini_agent.log）
- **会話履歴**: メモリ内のみ（永続化なし）

### **運用上の注意**
- **APIコスト**: Gemini API使用量に応じた課金
- **可用性**: Google Gemini APIサービス状況に依存
- **バージョン**: Gemini 2.5 Proの仕様変更影響の可能性

## 🔄 今後の拡張予定

### **機能拡張**
- **永続化オプション**: 会話履歴のDB保存機能
- **認証システム**: ユーザー認証・アクセス制御
- **カスタマイズ**: プロンプトテンプレートのカスタマイズ機能

### **統合拡張**
- **他エージェント連携**: Agent-to-Agent通信の実装
- **ワークフロー統合**: 複雑な業務プロセスとの統合
- **API拡張**: RESTful API・WebSocket対応

## 📋 開発履歴・コミット情報

- **実装完了**: 2025-01-XX
- **コミット**: `8980994` - "feat: implement Gemini-2.5-Pro A2A agent prototype with TDD"
- **品質保証**: 厳格品質保証システム v2.0 適用済み
- **テスト完了**: TDD準拠の包括的テストスイート完成

---

## 🔗 関連ドキュメント

- **[A2A Protocol実装ガイド](a2a_implementation_guide.md)**: 技術詳細・実装方法
- **[サンプルプログラム概要](../app/a2a_prototype/README.md)**: 使用方法・開発ガイド
- **[実装教訓集](../memory-bank/a2a_implementation_lessons_learned.md)**: 開発で得られた学習事項
- **[プロジェクト進捗](../memory-bank/progress.md)**: A2A調査プロジェクト全体記録

---

**作成日**: 2025-01-XX  
**対象**: 開発者・技術評価者  
**バージョン**: v1.0  
**ステータス**: 実装完了・運用可能 