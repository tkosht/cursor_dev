"""最もシンプルなLLM呼び出しテスト"""
import asyncio
import os
from dotenv import load_dotenv
from src.utils.llm_factory import create_llm

# .envファイルを読み込み
load_dotenv()

async def test_simple_llm_call():
    """シンプルなLLM呼び出しテスト"""
    print("=== シンプルなLLM呼び出しテスト ===")
    
    # LLMインスタンス作成
    llm = create_llm()
    print(f"LLM作成完了: {type(llm)}")
    
    # 簡単なプロンプト
    prompt = "こんにちは。1+1は何ですか？"
    print(f"プロンプト: {prompt}")
    
    try:
        # LLM呼び出し
        print("LLM呼び出し中...")
        response = await llm.ainvoke(prompt)
        print(f"応答: {response.content}")
        print("✅ LLM呼び出し成功！")
        return True
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        print(f"エラータイプ: {type(e)}")
        return False

if __name__ == "__main__":
    # 環境変数確認
    print("\n=== 環境変数確認 ===")
    print(f"GOOGLE_API_KEY: {'設定済み' if os.getenv('GOOGLE_API_KEY') else '未設定'}")
    print(f"OPENAI_API_KEY: {'設定済み' if os.getenv('OPENAI_API_KEY') else '未設定'}")
    
    # 実行
    success = asyncio.run(test_simple_llm_call())
    exit(0 if success else 1)