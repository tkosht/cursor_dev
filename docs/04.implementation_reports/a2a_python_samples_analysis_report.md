# Google A2A Python サンプルコード解析レポート

## 概要

本レポートは、Google A2A (Agent-to-Agent) プロトコルの公式サンプルリポジトリ（https://github.com/google-a2a/a2a-samples）に含まれるPythonサンプルコードの包括的な解析結果をまとめたものです。

## リポジトリ構造

```
a2a-samples/
├── samples/
│   └── python/
│       ├── agents/          # 各種フレームワークを使用したエージェント実装
│       ├── hosts/           # A2Aクライアントアプリケーション
│       └── common/          # 共通ユーティリティ（現在は非推奨）
├── demo/
├── tests/
└── noxfile.py
```

## 前提条件

- **Python**: 3.13以上
- **パッケージマネージャー**: UV
- **ライセンス**: Apache-2.0

## エージェントサンプル一覧

### 1. LangGraph エージェント (`langgraph/`)
- **用途**: 通貨変換ツールの実装
- **特徴**: 
  - マルチターン対話のサポート
  - ストリーミングレスポンス
  - Frankfurter APIを使用したリアルタイム為替レート取得
- **技術スタック**: LangGraph, LangChain, Google Generative AI

### 2. Google ADK エージェント (`google_adk/`)
- **用途**: 経費精算処理の自動化
- **特徴**:
  - Webフォームを使用したデータ収集
  - マルチターン対話による必要情報の収集
  - Google Vertex AIとの統合
- **技術スタック**: Google Agent Development Kit (ADK)

### 3. AG2 エージェント (`ag2/`)
- **用途**: MCPプロトコル対応エージェントのA2A公開
- **特徴**: MCPツールのA2Aプロトコルへのブリッジング
- **技術スタック**: AG2フレームワーク

### 4. Azure AI Foundry エージェント (`azureaifoundry_sdk/`)
- **用途**: Azure AI Foundryサービスとの統合
- **特徴**: Azure AIサービスのA2Aプロトコル対応
- **技術スタック**: Azure AI Foundry SDK

### 5. CrewAI エージェント (`crewai/`)
- **用途**: 画像生成
- **特徴**: マルチターン対話による画像生成パラメータの収集
- **技術スタック**: CrewAI フレームワーク

### 6. LlamaIndex エージェント (`llama_index_file_chat/`)
- **用途**: ファイル解析とコンテキストベースチャット
- **特徴**: アップロードされたファイルを解析し、その内容に基づいた対話
- **技術スタック**: LlamaIndex

### 7. Marvin エージェント (`marvin/`)
- **用途**: テキストからの構造化連絡先情報抽出
- **特徴**: 自然言語からの情報抽出と構造化
- **技術スタック**: Marvin フレームワーク

### 8. MindsDB エージェント (`mindsdb/`)
- **用途**: データベースへの自然言語クエリ
- **特徴**: Gemini 2.5 Flashを使用したSQL生成と実行
- **技術スタック**: MindsDB, Google Gemini

### 9. Semantic Kernel エージェント (`semantickernel/`)
- **用途**: 旅行代理店エージェント
- **特徴**: 旅行計画の作成と提案
- **技術スタック**: Microsoft Semantic Kernel

## ホストアプリケーション一覧

### 1. CLI ホスト (`hosts/cli/`)
- **用途**: コマンドラインからのA2Aエージェント操作
- **主要機能**:
  - エージェントカードの検索
  - タスクの作成と実行
  - ストリーミング/非ストリーミング通信
  - ファイル添付サポート
  - プッシュ通知リスナー

### 2. オーケストレーターエージェント (`hosts/orchestrator_agent/`)
- **用途**: 複数のリモートエージェントへのタスク委譲
- **主要機能**:
  - リモートエージェントのコレクション管理
  - タスクの分散と統合
  - Google ADK基盤

### 3. マルチエージェントWebホスト (`hosts/multiagent_web_host/`)
- **用途**: 複数エージェントとの対話を視覚化するWebアプリケーション
- **主要機能**:
  - テキスト、画像、Webフォームアーティファクトのレンダリング
  - タスク状態と履歴の可視化
  - 既知のエージェントカード表示

## 技術的実装パターン

### 1. エージェント宣言パターン
```python
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

capabilities = AgentCapabilities(
    streaming=True,
    pushNotifications=True
)

skill = AgentSkill(
    id='skill_id',
    name='Skill Name',
    description='What this skill does',
    tags=['tag1', 'tag2'],
    examples=['Example usage']
)

agent_card = AgentCard(
    name='Agent Name',
    description='Agent description',
    url=f'http://{host}:{port}/',
    version='1.0.0',
    capabilities=capabilities,
    skills=[skill]
)
```

### 2. サーバー実装パターン
```python
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

app = A2AStarletteApplication(
    agent=agent_implementation,
    agent_card=agent_card,
    task_store=InMemoryTaskStore(),
    request_handler=DefaultRequestHandler()
)
```

### 3. クライアント実装パターン
```python
from a2a.clients import AsyncA2AClient

client = AsyncA2AClient(base_url=agent_url, auth=auth)
task = await client.create_task(session_id=session_id)

# ストリーミング通信
async for response in client.stream_send_message(
    task_id=task.id,
    message=message
):
    # レスポンス処理

# 非ストリーミング通信
response = await client.send_message(
    task_id=task.id,
    message=message
)
```

## 主要な発見事項

### 1. フレームワーク非依存性
A2Aプロトコルは、LangGraph、CrewAI、LlamaIndex、Semantic Kernelなど、様々なAIフレームワークと統合可能な設計となっています。

### 2. 標準化された通信
すべてのエージェントが同じプロトコルで通信するため、異なるフレームワークで実装されたエージェント間でも相互運用が可能です。

### 3. 柔軟な実装オプション
- ストリーミング/非ストリーミング通信
- プッシュ通知
- セッション管理
- ファイル添付
- Webフォーム統合

### 4. エンタープライズ対応
- 認証サポート（APIキー、OAuth）
- エラーハンドリング
- タスク永続化オプション
- スケーラブルなアーキテクチャ

## 推奨される使用方法

1. **開発開始時**:
   - 最も近いユースケースのサンプルを選択
   - 該当するエージェントディレクトリに移動
   - `uv run .` でエージェントを起動
   - 別ターミナルでCLIホストを使用して対話

2. **本番環境への移行**:
   - InMemoryTaskStoreを永続化ストアに置き換え
   - 適切な認証メカニズムの実装
   - エラーハンドリングの強化
   - ロギングとモニタリングの追加

## 注意事項

- これらはサンプルコードであり、本番環境での使用を前提としていません
- 最新のA2A SDKを使用することを推奨（`pip install a2a-sdk`）
- Python 3.13以上が必要

## まとめ

Google A2Aプロトコルのサンプルは、エージェント間通信の標準化と相互運用性を実現する包括的な実装例を提供しています。様々なフレームワークとの統合例により、既存のAIシステムへのA2Aプロトコルの組み込みが容易になっています。