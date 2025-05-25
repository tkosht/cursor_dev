# A2A Prototype - Google公式a2a-sdk実装サンプル

このディレクトリには、Google公式a2a-sdk v0.2.4を使用したA2A（Agent-to-Agent）プロトコルのプロトタイプ実装が含まれています。

## 🎯 概要

- **目的**: A2Aプロトコルの技術的実現性の検証
- **使用ライブラリ**: Google公式 `a2a-sdk` v0.2.4
- **実装レベル**: 本格的なHTTPサーバー起動が可能

## 📁 ディレクトリ構成

```
app/a2a_prototype/
├── agents/                 # A2Aエージェント実装
│   ├── base_agent.py      # ベースエージェントクラス
│   ├── simple_agent.py    # シンプルなテストエージェント
│   └── __init__.py
├── utils/                  # ユーティリティ
│   ├── config.py          # エージェント設定管理
│   └── __init__.py
├── simple_test.py         # 基本動作確認テスト
├── test_simple_agent.py   # エージェント機能テスト
└── README.md              # このファイル
```

## 🚀 クイックスタート

### 1. 基本動作確認

まず、a2a-sdkの基本的な動作を確認：

```bash
# ワークスペースルートから実行
cd /home/devuser/workspace
python app/a2a_prototype/simple_test.py
```

**期待される出力:**
```
✅ A2A SDK imports successful
✅ AgentCard created successfully
✅ TaskState values (A2Aプロトコルで定義された全ての状態):
   - failed: 'failed' (失敗（※エラーではなく正常な状態の一つ）)
✅ EventQueue created successfully
   Queue closed: False (作成直後 - まだ開いている)
   Queue closed after close(): True (正常にクローズされました)
🎉 Basic tests completed successfully!
```

**注意**: 
- `failed`の表示: TaskStateの正常な状態の一つで、エラーではありません
- `Queue closed: False/True`: EventQueueのライフサイクルテストで、正常な動作です

### 2. エージェント機能テスト

SimpleTestAgentの機能をテスト：

```bash
python -m app.a2a_prototype.test_simple_agent
```

**期待される出力:**
```
=== Testing Agent Configuration ===
Config Name: simple-test-agent
Config Description: A simple test agent for A2A protocol verification

=== Testing Agent Card ===
Agent Name: simple-test-agent
Skills:
  - echo: Echo back the user's message
  - greet: Greet the user

=== Testing User Input Processing ===
Input: 'hello'
Response: Hello! I'm simple-test-agent. How can I help you today?
```

### 3. HTTPサーバー起動テスト（準備中）

実際のA2AエンドポイントとしてHTTPサーバーを起動：

```bash
# 注意: 現在はBaseAgentクラスの修正が必要
python -m app.a2a_prototype.agents.simple_agent
```

## 🏗️ 実装されている機能

### BaseA2AAgent クラス

- **場所**: `agents/base_agent.py`
- **機能**: A2Aプロトコル準拠のベースクラス
- **特徴**:
  - AgentExecutorインターフェースの実装
  - エージェントカードの自動生成
  - リクエスト処理とイベント管理
  - ヘルスチェック機能

### SimpleTestAgent クラス

- **場所**: `agents/simple_agent.py`
- **機能**: テスト用の具体的なエージェント実装
- **提供スキル**:
  - `echo`: メッセージをエコーバック
  - `greet`: ユーザーへの挨拶
- **対応コマンド**:
  - `hello`/`hi`: 挨拶
  - `echo <message>`: メッセージエコー
  - `status`: エージェント状態確認
  - `help`: ヘルプ表示

### AgentConfig クラス

- **場所**: `utils/config.py`
- **機能**: エージェント設定の管理
- **プリセット**: 天気エージェント、チャットエージェント、計算エージェント

## 🔧 技術仕様

### 使用技術

- **Python**: 3.10+
- **A2A SDK**: v0.2.4 (Google公式)
- **Webフレームワーク**: Starlette (a2a-sdk経由)
- **非同期処理**: asyncio
- **型システム**: Pydantic v2

### A2Aプロトコル対応

- ✅ Agent Card (`/.well-known/agent.json`)
- ✅ Task lifecycle management
- ✅ Event-driven architecture
- ✅ JSON-RPC 2.0 over HTTP
- ✅ Server-Sent Events (SSE)

## 🧪 テストの実行

### 基本テストスイート

```bash
# 基本動作確認
python app/a2a_prototype/simple_test.py

# エージェント機能テスト
python -m app.a2a_prototype.test_simple_agent
```

### 個別テスト

```bash
# AgentCard作成テスト
python -c "
from app.a2a_prototype.agents.simple_agent import create_test_agent
agent = create_test_agent(8001)
print(f'Agent: {agent.config.name}')
print(f'Skills: {[s.name for s in agent.agent_card.skills]}')
"

# ユーザー入力処理テスト
python -c "
import asyncio
from app.a2a_prototype.agents.simple_agent import create_test_agent

async def test():
    agent = create_test_agent(8001)
    response = await agent.process_user_input('hello world')
    print(f'Response: {response}')

asyncio.run(test())
"
```

## 🐛 トラブルシューティング

### よくある問題

1. **ImportError: cannot import name 'A2AStarletteApplication'**
   - 原因: BaseAgentクラスのインポートパスが古い
   - 解決: 正しいパス `from a2a.server.apps.starlette_app import A2AStarletteApplication` を使用

2. **ModuleNotFoundError: No module named 'agents'**
   - 原因: 相対インポートの問題
   - 解決: ワークスペースルートから `python -m app.a2a_prototype.XXX` で実行

3. **AgentCard validation error**
   - 原因: AgentCapabilitiesの構造が不正
   - 解決: 空の辞書 `{}` または適切なAgentCapabilitiesオブジェクトを使用

### デバッグ方法

```bash
# ログレベルを上げて実行
PYTHONPATH=/home/devuser/workspace python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# テストコードを実行
"

# インポートテスト
python -c "
try:
    from a2a.server.apps.starlette_app import A2AStarletteApplication
    print('✅ A2AStarletteApplication import OK')
except ImportError as e:
    print(f'❌ Import failed: {e}')
"
```

## 📝 次のステップ

1. **HTTPサーバー起動テスト**: BaseAgentクラスの修正完了後
2. **Agent Card取得**: `curl http://localhost:8001/.well-known/agent.json`
3. **JSON-RPC通信テスト**: 実際のA2A通信の検証
4. **複数エージェント連携**: Agent-to-Agent通信のテスト

## 🔗 関連リンク

- [A2A Protocol Specification](https://github.com/google/A2A)
- [Google a2a-sdk Documentation](https://pypi.org/project/a2a-sdk/)
- [Project Memory Bank](../../memory-bank/README.md)

---

**注意**: このプロトタイプは技術検証用です。本番環境での使用前に適切なセキュリティ設定とエラーハンドリングを追加してください。 