# A2A Protocol Investigation - Prototype

このディレクトリには、Google公式a2a-sdk v0.2.4を使用したA2A（Agent-to-Agent）プロトコルの実機調査・検証用プロトタイプが含まれています。

## 📁 プロジェクト構造

```
./
├── examples/                        # 🆕 動作確認・デモ用スクリプト
│   ├── a2a_basic_check.py              # A2A SDK基本動作確認
│   └── simple_agent_demo.py            # SimpleTestAgentデモ
├── tests/                           # 🆕 TDD準拠のpytestテスト
│   ├── conftest.py                     # pytest共通設定・フィクスチャ
│   ├── unit/                           # 単体テスト（高速・独立）
│   │   ├── test_types/                 # a2a.types テスト
│   │   │   └── test_agent_skill.py     # AgentSkill TDDテスト
│   │   └── test_agents/                # エージェント単体テスト
│   │       └── test_simple_agent.py    # SimpleTestAgent TDDテスト
│   ├── integration/                    # 統合テスト（中速・依存あり）
│   └── e2e/                           # E2Eテスト（低速・完全シナリオ）
├── app/a2a_prototype/               # アプリケーションコード
│   ├── agents/                         # エージェント実装
│   │   ├── base_agent.py               # 基底エージェントクラス
│   │   ├── simple_agent.py             # 🔧 SimpleTestAgent実装 (基本動作確認用)
│   │   └── gemini_agent.py             # 🧠 GeminiA2AAgent実装 (Gemini 2.5 Pro AI)
│   └── utils/                          # ユーティリティ
│       ├── config.py                   # エージェント設定管理
│       ├── gemini_client.py            # Gemini APIクライアント
│       └── gemini_config.py            # Gemini設定管理
└── docs/                            # ドキュメント
    ├── a2a_implementation_guide.md     # 技術実装ガイド
    └── development_rules/              # 開発ルール・ガイドライン
        └── tdd_implementation_guide.md # TDD実践ガイド
```

## 🔄 ファイル名整理について

### 整理前（問題があった構造）

```
❌ app/a2a_prototype/simple_test.py     # 動作確認だがpytestっぽい名前
❌ app/a2a_prototype/test_simple_agent.py # pytestテストだが配置場所が不適切
```

**問題点**:
- pytest標準の命名規則に非準拠
- 動作確認スクリプトとpytestテストが混在
- TDD実践になっていない甘いテスト
- アプリケーションディレクトリにテストファイルが配置

### 整理後（適切な構造）

```
✅ examples/a2a_basic_check.py          # 明確に動作確認用
✅ examples/simple_agent_demo.py        # 明確にデモ用
✅ tests/unit/test_types/test_agent_skill.py     # TDD準拠のpytestテスト
✅ tests/unit/test_agents/test_simple_agent.py   # TDD準拠のpytestテスト
```

**改善点**:
- 役割が明確な命名・配置
- pytest標準ディレクトリ構造準拠
- TDD（Test Driven Development）実践
- 単体・統合・E2Eテストの階層化

## 🔧 エージェント種類の違い ⭐ **重要**

このプロジェクトには**2つの全く異なるエージェント**が実装されています：

### **🔧 Simple Test Agent (simple_agent.py)** - プロトコル学習用

**何ができるか**: A2Aプロトコルの基本的な動作を**固定応答**で確認できる

#### 📝 **実際の対話例**
```
入力: "hello"
応答: "Hello! I'm simple-test-agent. How can I help you today?"

入力: "echo test message"
応答: "Echo: test message"

入力: "status"
応答: "I'm simple-test-agent running on http://localhost:8001. Status: OK"

入力: "help"
応答: "Available commands for simple-test-agent:
       - hello/hi: Greet the agent
       - echo <message>: Echo back your message
       - status: Check agent status
       - help: Show this help message"

入力: "anything else"
応答: "I received: 'anything else'. Try 'help' for available commands."
```

#### 🎯 **この実装が参考になる理由**
- **A2Aプロトコルの学習**: JSON-RPC 2.0ベースの基本的な通信フローを理解
- **エージェント実装の基礎**: BaseA2AAgentの継承パターンを学習
- **デバッグ・テスト**: プロトコル通信のトラブルシューティング手法を習得

---

### **🧠 Gemini AI Agent (gemini_agent.py)** - 実用AI対話システム

**何ができるか**: Google Gemini 2.5 Proによる**高度なAI対話**と文脈理解

#### 🤖 **実際の対話例**
```
入力: "Pythonでファイル処理をする効率的な方法を教えて"
応答: "Pythonでファイル処理を効率的に行う方法をいくつか紹介します。
       
       1. **withステートメント使用**:
       with open('file.txt', 'r', encoding='utf-8') as f:
           content = f.read()
       
       2. **pathlib使用**:
       from pathlib import Path
       file = Path('file.txt')
       content = file.read_text(encoding='utf-8')
       
       ..." (詳細な説明が続く)

入力: "さっきのpathlib、実際のコード例で見せて"
応答: "先ほどのpathlibについて、具体的なコード例をお見せします..."
       (会話履歴を考慮した追加説明)

入力: "status"
応答: "🤖 gemini-a2a-agent
       📡 URL: http://localhost:8004
       🧠 Model: gemini-2.5-pro
       🌡️ Temperature: 0.7
       💚 Status: ✅ OK
       💬 Context: 4 messages
       🔑 API Key: goo***...***xyz"

入力: "clear"
応答: "✅ 会話履歴をクリアしました。新しい会話を始めましょう！"
```

#### 🎯 **この実装が参考になる理由**
- **企業レベルAI統合**: APIキー管理・エラーハンドリング・セキュリティ配慮
- **会話システム設計**: 履歴管理・文脈考慮・UX最適化パターン
- **本格的サービス構築**: プロダクション品質のエージェント実装手法

---

## 🚀 クイックスタート

### 1. 基本動作確認（手動テスト）

#### **📋 A2A SDK基本動作確認 (a2a_basic_check.py)**
```bash
python examples/a2a_basic_check.py
```

**何をテストするか:**
- ✅ Google公式a2a-sdk v0.2.4のインポート確認
- ✅ AgentCard（エージェント情報カード）の作成・構造確認
- ✅ TaskState（タスク状態管理）の全状態値確認
- ✅ EventQueue（非同期イベント処理）の作成・クローズ確認

**期待される出力例:**
```
✅ A2A SDK imports successful
✅ AgentCard created successfully:
   Name: test-agent
   Description: A simple test agent
   URL: http://localhost:8001
   Skills: 1
✅ TaskState values (A2Aプロトコルで定義された全ての状態):
   - submitted: 'submitted' (投入済み)
   - working: 'working' (実行中)
   - completed: 'completed' (完了)
✅ EventQueue created and managed successfully
```

#### **🎭 SimpleTestAgentデモ (simple_agent_demo.py)**
```bash
python examples/simple_agent_demo.py
```

**何をテストするか:**
- ✅ SimpleTestAgentの作成・設定確認
- ✅ エージェントカード（JSON形式）の出力確認
- ✅ 各種入力に対する応答動作確認（hello, echo, status, help等）

**期待される出力例:**
```
=== Testing Agent Configuration ===
Config Name: simple-test-agent
Config URL: http://localhost:8001

=== Testing Agent Card ===
Agent Name: simple-test-agent
Skills:
  - echo: Echo back the user's message
  - greet: Greet the user

=== Testing User Input Processing ===
Input: 'hello'
Response: Hello! I'm simple-test-agent. How can I help you today?

Input: 'echo test message'
Response: Echo: test message
```

### 2. エージェント起動

#### **🔧 Simple Test Agent起動**
```bash
# 基本動作確認用エージェント（AIなし）
python app/a2a_prototype/agents/simple_agent.py
# → http://localhost:8001 で起動
```

#### **🧠 Gemini AI Agent起動**
```bash
# 1. API Key設定（必須）
export GEMINI_API_KEY="your-gemini-api-key"

# 2. Gemini AIエージェント起動
python scripts/run_gemini_agent.py
# → http://localhost:8004 で起動

# 3. 動作確認
curl http://localhost:8004/.well-known/agent.json
```

### 3. TDD準拠のテスト実行

```bash
# 単体テストのみ（高速）
poetry run pytest tests/unit/ -v

# 全テスト実行
poetry run pytest tests/ -v

# カバレッジ付きテスト実行
poetry run pytest tests/ --cov=src --cov-report=html

# テストカテゴリ別実行
poetry run pytest tests/unit/ -m unit
poetry run pytest tests/integration/ -m integration
```

## 🎯 TDD実践について

このプロジェクトでは **Test Driven Development (TDD)** を厳格に実践しています：

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通すための最小限の実装
3. **Refactor**: コードを改善しつつテストが通ることを確認

詳細は [`docs/development_rules/tdd_implementation_guide.md`](../../docs/development_rules/tdd_implementation_guide.md) を参照してください。

## 📊 テスト品質指標

- **単体テスト**: 最低90%、目標95% カバレッジ
- **統合テスト**: 主要パス100%
- **E2Eテスト**: クリティカルパス100%
- **実行時間**: 単体テスト<10秒、統合テスト<30秒、E2E<120秒

## 🔧 開発ワークフロー

### 新機能追加時

```bash
# 1. テストファースト：失敗するテストを書く
echo "def test_new_feature(): assert False" >> tests/unit/test_new_feature.py

# 2. テスト実行（Red）
poetry run pytest tests/unit/test_new_feature.py

# 3. 最小実装（Green）
# 実装コードを作成してテストを通す

# 4. リファクタリング（Refactor）
# コードを改善しつつテストが通ることを確認
```

### バグ修正時

```bash
# 1. 再現テストを先に書く
# 2. テストが失敗することを確認
# 3. バグを修正
# 4. テストが通ることを確認
```

## 💡 学習事項

このプロジェクトから得られた重要な学習事項は以下にまとめられています：

- [`memory-bank/a2a_implementation_lessons_learned.md`](../../memory-bank/a2a_implementation_lessons_learned.md)
- A2A公式SDKの正確なAPI仕様確認方法
- Pydanticバリデーションエラーの体系的解析
- TDD実践の重要性と具体的手法

## 🔗 関連ドキュメント

### **🔧 Simple Agent関連**
- [A2A実装技術ガイド](../../docs/a2a_implementation_guide.md): 基本的なA2A実装方法
- [TDD実践ガイドライン](../../docs/development_rules/tdd_implementation_guide.md): テスト駆動開発手法

### **🧠 Gemini Agent関連**
- [Gemini A2A Agent詳細仕様書](../../docs/gemini_a2a_agent_specification.md): **Gemini Agent専用仕様** ⭐
- [Gemini Agent実行スクリプト](../../scripts/run_gemini_agent.py): 起動・設定方法

### **📚 学習・教訓**
- [プロジェクト学習事項](../../memory-bank/a2a_implementation_lessons_learned.md): 実装で得られた知見

---

## ⚙️ 使い分けガイド ⭐ **まとめ**

### **🔧 Simple Test Agent**
**こんな時に使う:**
- A2Aプロトコルの基本を学習したい
- 通信フローの動作確認・デバッグを行いたい
- AIを使わずシンプルな応答パターンをテストしたい
- プロトコルの理解を深めたい

### **🧠 Gemini AI Agent**
**こんな時に使う:**
- 実用的なAI対話システムを構築したい
- 高度な質問応答機能を実装したい
- 会話履歴を考慮した文脈理解が必要
- プロダクションレベルのエージェントシステムを検討している

### **📋 動作確認スクリプト**
**こんな時に使う:**
- A2A SDKが正しくインストールされているか確認したい
- エージェントの基本機能を一通りテストしたい
- 開発環境のセットアップを検証したい

---

**注意**: このプロトタイプは調査・学習目的です。本番環境での使用前に追加の検証・テストが必要です。 