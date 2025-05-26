# cursor_dev - AI Research & Development Project

AIエージェント技術の研究・開発プロジェクトです。安全で標準的なプロトコルとライブラリを使用した実装を行います。

## 🚨 セキュリティ注意事項

**重要**: このプロジェクトでは、**公式かつ信頼できるライブラリのみ**を使用します。
- 非公式のサードパーティライブラリは重大なセキュリティリスクを伴います
- 常に公式ドキュメントと公式リポジトリから提供されるライブラリを使用してください

## 🎯 プロジェクト概要

### 現在のステータス
- **🎉 A2A調査プロジェクト完了**: 5フェーズにわたる包括的調査完了
- **✅ 最終報告書作成済み**: 意思決定支援資料完成
- **✅ 技術実装検証済み**: Google公式SDKによる実装確認
- **✅ コード品質確保**: 高品質なシステム構築（カバレッジ92.6%）

### A2A調査プロジェクト成果
- **総合推奨度**: 3/5（条件付き採用推奨）
- **技術的実現可能性**: ⭐⭐⭐⭐⭐ (5/5)
- **実用性**: ⭐⭐⭐⭐ (4/5)  
- **将来性**: ⭐⭐⭐ (3/5)

## 🚀 開発環境

### 必要な環境
- Python 3.10+
- Poetry
- VSCode Dev Container（推奨）

### 環境構築

```bash
# 1. 依存関係のインストール
poetry install

# 2. 環境変数設定（重要）
# .envファイルを作成
cp .env.example .env

# .envファイルを編集してAPIキーを設定
# GEMINI_API_KEY=your-actual-api-key-here
```

### 🔑 API キー設定

#### Google Gemini API キー（必須）

1. **APIキー取得**: [Google AI Studio](https://makersuite.google.com/app/apikey) でAPIキーを取得
2. **環境変数設定**: 以下のいずれかの方法で設定

##### 方法1: .envファイル使用（推奨）
```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集
GEMINI_API_KEY=your-actual-api-key-here
```

##### 方法2: 直接環境変数設定
```bash
# 一時的に設定
export GEMINI_API_KEY="your-actual-api-key-here"

# 永続的に設定（.bashrc/.zshrcに追加）
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.bashrc
```

#### 設定確認
```bash
# APIキーが設定されているか確認
echo $GEMINI_API_KEY

# エージェント起動（APIキー設定状況も表示される）
python scripts/run_gemini_agent.py
```

## 📁 プロジェクト構造

```
cursor_dev/
├── memory-bank/                # AIの記憶領域
├── docs/                       # プロジェクトドキュメント
├── .devcontainer/              # Dev Container設定
└── README.md
```

## 💻 実際に何ができるサンプルコード ⭐ **NEW**

### **🔧 Simple Test Agent** - A2Aプロトコル学習用
固定応答によるプロトコル動作確認。AIは使用せず、基本的な通信フローを理解できる。

**対話例:**
```
あなた: "hello"
エージェント: "Hello! I'm simple-test-agent. How can I help you today?"

あなた: "echo Python is great!"
エージェント: "Echo: Python is great!"

あなた: "status"
エージェント: "I'm simple-test-agent running on http://localhost:8001. Status: OK"
```

**実行方法:** `python app/a2a_prototype/agents/simple_agent.py`

### **🧠 Gemini AI Agent** - 実用的AI対話システム
Google Gemini 2.5 Pro搭載。会話履歴を記憶して高度な対話が可能。

**対話例:**
```
あなた: "Pythonでファイル処理の効率的な方法を教えて"
Gemini: "Pythonでファイル処理を効率的に行う方法をいくつか紹介します。
        1. withステートメント使用:
        with open('file.txt', 'r') as f:
            content = f.read()
        2. pathlib使用:
        from pathlib import Path..."

あなた: "さっきのpathlibについてもう少し詳しく"
Gemini: "先ほどのpathlibについて、より詳細に説明します..." (履歴を考慮)
```

**実行方法:** `python scripts/run_gemini_agent.py` (API Key設定必須)

---

## 📖 ドキュメント

### 🎯 A2A調査最終報告書
- **[📊 Executive Summary](docs/05_final_report/executive_summary.md)**: 意思決定者向け5分読了資料
- **[📋 包括的調査報告書](docs/05_final_report/a2a_comprehensive_evaluation_report.md)**: 詳細な技術評価・推奨事項
- **[🔍 プロトコル比較表](docs/04_comparative_analysis/protocol_comparison_table.md)**: 他技術との詳細比較

### 基本ドキュメント
- **[memory-bank/projectbrief.md](memory-bank/projectbrief.md)**: プロジェクト概要
- **[memory-bank/progress.md](memory-bank/progress.md)**: 全フェーズの進捗・成果記録
- **[memory-bank/activeContext.md](memory-bank/activeContext.md)**: プロジェクト完了状況

### 技術実装ドキュメント
- **[docs/a2a_implementation_guide.md](docs/a2a_implementation_guide.md)**: A2A実装ガイド
- **[docs/gemini_a2a_agent_specification.md](docs/gemini_a2a_agent_specification.md)**: Gemini A2A Agent詳細仕様書 🧠 **NEW**
- **[memory-bank/a2a_implementation_lessons_learned.md](memory-bank/a2a_implementation_lessons_learned.md)**: 実装教訓集
- **[app/a2a_prototype/](app/a2a_prototype/)**: 実装サンプルコード - **詳細な動作説明追加** ⭐
- **[scripts/run_gemini_agent.py](scripts/run_gemini_agent.py)**: Gemini Agent実行スクリプト 🧠 **NEW**

### セットアップドキュメント
- **[docs/setup/api_key_configuration.md](docs/setup/api_key_configuration.md)**: APIキー設定の詳細ガイド
- **[.env.example](.env.example)**: 環境変数設定サンプル

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

## 🔒 セキュリティポリシー

1. **公式ライブラリのみ使用**: 信頼できる公式ソースからのみライブラリをインストール
2. **定期的な依存関係チェック**: `poetry show --outdated` による脆弱性確認
3. **機密情報の管理**: 環境変数・.envファイルによる適切な管理
4. **コード品質の維持**: linter・型チェック・テストの継続的実行

## 🤝 開発プロセス

このプロジェクトでは、Memory Bank駆動の開発プロセスを採用しています：

1. **調査・計画**: memory-bank/に知識・計画を蓄積
2. **実装**: 段階的な実装とテスト
3. **文書化**: 実装結果をmemory-bankに反映
4. **品質管理**: linter・テストによる品質確保

---

**🔒 セキュリティファースト**: 安全で信頼できる開発を最優先に進めています。
