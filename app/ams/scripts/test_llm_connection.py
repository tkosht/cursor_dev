"""LLM接続テスト - 実際のAPI呼び出し確認"""
import asyncio
import os
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# .envファイルを読み込み
load_dotenv()

async def test_basic_connection():
    """基本的な接続テスト"""
    print("=== 基本的なLLM接続テスト ===")

    # API キーの確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ エラー: GOOGLE_API_KEY が設定されていません")
        print("対処法: .envファイルに GOOGLE_API_KEY=your-key-here を追加してください")
        return False

    print(f"✅ API Key 検出: {api_key[:10]}...{api_key[-4:]}")

    try:
        # LLM作成
        print("\n📡 LLMインスタンス作成中...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        print("✅ LLMインスタンス作成完了")

        # テスト呼び出し1: シンプルな質問
        print("\n🧪 テスト1: シンプルな計算")
        start_time = time.time()
        response = await llm.ainvoke("1+1は何ですか？短く答えてください。")
        elapsed = time.time() - start_time

        print(f"✅ 応答: {response.content}")
        print(f"⏱️  処理時間: {elapsed:.2f}秒")

        # テスト呼び出し2: 日本語処理
        print("\n🧪 テスト2: 日本語処理")
        start_time = time.time()
        response = await llm.ainvoke("「こんにちは」を英語に翻訳してください。")
        elapsed = time.time() - start_time

        print(f"✅ 応答: {response.content}")
        print(f"⏱️  処理時間: {elapsed:.2f}秒")

        # メタデータの確認
        if hasattr(response, 'response_metadata'):
            print("\n📊 メタデータ:")
            print(f"   - モデル: {response.response_metadata.get('model_name', 'N/A')}")
            print(f"   - トークン使用量: {response.response_metadata.get('token_usage', 'N/A')}")

        print("\n✅ すべてのテストが成功しました！")
        return True

    except Exception as e:
        print("\n❌ エラーが発生しました:")
        print(f"   タイプ: {type(e).__name__}")
        print(f"   詳細: {e}")

        # エラー別の対処法
        if "API key not valid" in str(e):
            print("\n💡 対処法: APIキーが無効です。" +
                  "Google AI Studioで新しいキーを生成してください。")
        elif "quota" in str(e).lower():
            print("\n💡 対処法: APIの利用制限に達しました。" +
                  "しばらく待ってから再試行してください。")
        else:
            print("\n💡 対処法: エラーの詳細を確認し、" +
                  "ネットワーク接続やAPI設定を確認してください。")

        return False

async def test_with_ams_context():
    """AMSコンテキストでのテスト"""
    print("\n\n=== AMSコンテキストでのLLMテスト ===")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ API キーが設定されていません")
        return False

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )

        # AMSで使用する典型的なプロンプト
        prompt = """
        以下の短い記事を分析してください：

        「AIアシスタントが日常業務を効率化」
        新しいAIアシスタントにより、文書作成や情報検索が大幅に高速化されました。

        この記事の主要なトピックを1つ挙げてください。
        """

        print("🧪 AMSスタイルのプロンプトをテスト中...")
        start_time = time.time()
        response = await llm.ainvoke(prompt)
        elapsed = time.time() - start_time

        print(f"✅ 応答: {response.content}")
        print(f"⏱️  処理時間: {elapsed:.2f}秒")

        # コスト推定
        # 概算: 入力100トークン + 出力50トークン
        estimated_cost = (100 * 0.000000075) + (50 * 0.0000003)  # gemini-1.5-flash pricing
        print(f"💰 推定コスト: ${estimated_cost:.6f}")

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def main():
    """メイン実行関数"""
    print("🚀 LangChain + Google Gemini API 接続テスト開始")
    print("=" * 50)

    # 基本テスト
    basic_success = await test_basic_connection()

    if basic_success:
        # AMSコンテキストテスト
        ams_success = await test_with_ams_context()

        if ams_success:
            print("\n\n✨ すべてのテストが成功しました！")
            print("次のステップ: 小規模統合テストの実行")
            return True

    print("\n\n❌ テストに失敗しました。エラーを確認してください。")
    return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
