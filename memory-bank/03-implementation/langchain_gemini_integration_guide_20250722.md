# LangChain + Google Gemini API 統合実装ガイド

## 📅 作成日: 2025-07-22
## 🏷️ タグ: langchain, gemini, google-ai, llm, integration, real-api-calls

## 🎯 目的
実際のLLM API呼び出しを使用したLangChain + Google Gemini統合の正しい実装方法を記録

## 📚 参照情報
- WebSearch結果: LangChain公式ドキュメント
- 内部ドキュメント: @docs/langgraph-agent-communication-design.md
- 内部ドキュメント: @docs/langgraph-implementation-guide.md

## 🔧 実装方法

### 1. 必要なパッケージのインストール
```bash
pip install langchain langchain-google-genai google-generativeai python-dotenv
```

### 2. 環境変数の設定
```python
# .env ファイル
GOOGLE_API_KEY=your-api-key-here
```

### 3. 基本的なLLM呼び出し実装
```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 環境変数の読み込み
load_dotenv()

# LLMインスタンスの作成
def create_llm():
    """Google Gemini LLMインスタンスを作成"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
        max_tokens=2048
    )

# 同期呼び出し
def simple_llm_call():
    llm = create_llm()
    response = llm.invoke("こんにちは。1+1は何ですか？")
    print(f"Response: {response.content}")
    return response

# 非同期呼び出し
async def async_llm_call():
    llm = create_llm()
    response = await llm.ainvoke("こんにちは。1+1は何ですか？")
    print(f"Response: {response.content}")
    return response
```

### 4. LangGraphでの統合
```python
from langgraph.graph import StateGraph, MessagesState
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: dict

async def llm_node(state: State) -> dict:
    """LangGraphノード内でのLLM呼び出し"""
    llm = create_llm()
    
    # 最新のメッセージを取得
    last_message = state["messages"][-1] if state["messages"] else "Hello"
    
    # LLM呼び出し
    response = await llm.ainvoke(last_message)
    
    # 状態の更新
    return {
        "messages": [("assistant", response.content)],
        "context": {"llm_called": True}
    }
```

### 5. エラーハンドリング
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_llm_call(prompt: str):
    """再試行付きのLLM呼び出し"""
    try:
        llm = create_llm()
        response = await llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        print(f"LLM呼び出しエラー: {e}")
        raise
```

## 🧪 動作確認済みコード

### 最小限の動作確認スクリプト
```python
"""test_llm_connection.py"""
import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

async def test_connection():
    """接続テスト"""
    print("=== LLM接続テスト ===")
    
    # API キーの確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY が設定されていません")
        return False
    
    print(f"✅ API Key: {api_key[:10]}...")
    
    try:
        # LLM作成
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key
        )
        
        # テスト呼び出し
        response = await llm.ainvoke("Hello, this is a test. Reply with 'OK'.")
        print(f"✅ Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
```

## 💰 コスト見積もり

| モデル | 入力 | 出力 | 推定コスト/1000呼び出し |
|--------|------|------|------------------------|
| gemini-1.5-flash | $0.075/1M tokens | $0.30/1M tokens | ~$2-5 |
| gemini-1.5-pro | $1.25/1M tokens | $5.00/1M tokens | ~$20-50 |

## ⚠️ 注意事項

1. **API キー管理**
   - 絶対にコードに直接記載しない
   - .envファイルは.gitignoreに追加
   - 環境変数経由でのみアクセス

2. **レート制限**
   - gemini-1.5-flash: 60 RPM (requests per minute)
   - 再試行ロジックを実装

3. **モック使用禁止**
   - 統合テストでは実際のAPI呼び出しを使用
   - 小規模テスト（3-5呼び出し）で動作確認

## 🔗 関連リンク
- [LangChain Google Generative AI Documentation](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)
- [Google AI Studio](https://ai.google.dev/)
- [Gemini API Pricing](https://ai.google.dev/pricing)