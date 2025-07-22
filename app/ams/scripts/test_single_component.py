"""単一コンポーネントテスト - 実際のLLM呼び出し確認"""
import asyncio
import os
import sys
import time

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.deep_context_analyzer import DeepContextAnalyzer

# 環境変数読み込み
load_dotenv()

# テスト用の短い記事
TEST_ARTICLE = """
AIアシスタントが業務効率を向上させます。
自然な会話で操作でき、24時間利用可能です。
"""

async def test_analyzer_only():
    """DeepContextAnalyzerのみをテスト"""
    print("🧪 DeepContextAnalyzer 単体テスト（実API）")
    print("=" * 50)

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY が設定されていません")
        return False

    try:
        analyzer = DeepContextAnalyzer()

        print("📊 記事分析開始...")
        print(f"記事: {TEST_ARTICLE[:50]}...")

        start_time = time.time()
        context = await analyzer.analyze_article_context(TEST_ARTICLE)
        elapsed = time.time() - start_time

        print(f"\n✅ 分析完了 ({elapsed:.2f}秒)")
        print(f"複雑度スコア: {context.get('complexity_score', 0):.2f}")
        print(f"リーチポテンシャル: {context.get('reach_potential', 0):.2f}")

        # コンテキストの一部を表示
        if 'core_context' in context:
            domain = context['core_context'].get('domain_analysis', {})
            print("\nドメイン分析:")
            print(f"  主要ドメイン: {domain.get('primary_domain', 'N/A')}")

        print("\n💰 推定API呼び出し: 2回（コア分析 + 隠れた次元）")

        return True

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_analyzer_only())
    print(f"\n{'✅ 成功' if success else '❌ 失敗'}")
    exit(0 if success else 1)
