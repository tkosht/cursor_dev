"""小規模統合テスト - 実際のLLM呼び出しで3ペルソナ生成"""
import asyncio
import json
import os
import time

from dotenv import load_dotenv

from src.agents.deep_context_analyzer import DeepContextAnalyzer
from src.agents.persona_generator import PersonaGenerator
from src.agents.population_architect import PopulationArchitect

# 環境変数読み込み
load_dotenv()

# テスト用の短い記事
TEST_ARTICLE = """
# AIアシスタントの新機能発表

本日、革新的なAIアシスタント機能を発表しました。
この機能により、日常業務の効率が大幅に向上します。

主な特徴：
- 自然な会話での操作
- マルチタスク対応
- 24時間利用可能

ユーザーからは「使いやすい」「時間の節約になる」といった
ポジティブなフィードバックを多数いただいています。
"""

async def run_small_scale_test():
    """小規模統合テスト実行"""
    print("🚀 AMS小規模統合テスト開始（3ペルソナ、実API呼び出し）")
    print("=" * 60)

    # API キー確認
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ エラー: GOOGLE_API_KEY が設定されていません")
        return False

    # 実行時間とAPIコールを追跡
    start_time = time.time()
    api_call_count = 0

    try:
        # Phase 1: 記事分析
        print("\n📊 Phase 1: 記事コンテキスト分析")
        print("-" * 40)

        analyzer = DeepContextAnalyzer()
        analysis_start = time.time()

        context = await analyzer.analyze_article_context(TEST_ARTICLE)

        analysis_time = time.time() - analysis_start
        api_call_count += 2  # Core + Hidden dimensions

        print(f"✅ 分析完了 ({analysis_time:.2f}秒)")
        print(f"   - 複雑度スコア: {context.get('complexity_score', 0):.2f}")
        print(f"   - リーチポテンシャル: {context.get('reach_potential', 0):.2f}")
        # 主要ドメインを取得（ネストが深いため分割）
        core_context = context.get('core_context', {})
        domain_analysis = core_context.get('domain_analysis', {})
        primary_domain = domain_analysis.get('primary_domain', 'N/A')
        print(f"   - 主要ドメイン: {primary_domain}")

        # Phase 2: 人口構造設計
        print("\n👥 Phase 2: ペルソナ人口構造設計（3体）")
        print("-" * 40)

        architect = PopulationArchitect()
        architect_start = time.time()

        population = await architect.design_population_hierarchy(
            context,
            target_size=3
        )

        architect_time = time.time() - architect_start
        api_call_count += 2  # Major segments + sub-segments

        print(f"✅ 人口構造設計完了 ({architect_time:.2f}秒)")
        print(f"   - 主要セグメント数: {len(population['hierarchy']['major_segments'])}")
        print(f"   - ペルソナスロット数: {len(population['hierarchy']['persona_slots'])}")

        # 主要セグメント表示
        for seg in population['hierarchy']['major_segments'][:3]:
            print(f"   - {seg['name']}: {seg['percentage']:.1f}%")

        # Phase 3: ペルソナ生成
        print("\n🎭 Phase 3: 個別ペルソナ生成")
        print("-" * 40)

        generator = PersonaGenerator()
        generator_start = time.time()

        personas = await generator.generate_personas(
            article_content=TEST_ARTICLE,
            analysis_results=context,
            count=3
        )

        generator_time = time.time() - generator_start
        api_call_count += len(personas)  # 各ペルソナごとに1回

        print(f"✅ {len(personas)}体のペルソナ生成完了 ({generator_time:.2f}秒)")

        # ペルソナ詳細表示
        for i, persona in enumerate(personas, 1):
            print(f"\n   📋 ペルソナ {i}:")
            print(f"      - 職業: {persona.occupation}")
            print(f"      - 年齢: {persona.age}")
            print(f"      - 関心事: {', '.join(persona.interests[:3])}")
            print(f"      - 影響力スコア: {persona.influence_score:.2f}")
            print(f"      - シェア可能性: {persona.content_sharing_likelihood:.2f}")

        # 総括
        total_time = time.time() - start_time

        print("\n" + "=" * 60)
        print("✨ テスト完了サマリー")
        print(f"   - 総実行時間: {total_time:.2f}秒")
        print(f"   - API呼び出し回数: {api_call_count}回")
        print(f"   - 推定コスト: ${api_call_count * 0.000022:.6f}")
        print(f"   - 1ペルソナあたり時間: {total_time/3:.2f}秒")

        # 成功基準チェック
        print("\n🎯 成功基準チェック:")
        print("   ✅ 3ペルソナ生成: 完了")
        print(f"   {'✅' if total_time < 60 else '❌'} 実行時間 < 60秒: {total_time:.2f}秒")
        print(f"   {'✅' if api_call_count <= 10 else '⚠️'} API呼び出し ≤ 10回: {api_call_count}回")

        # 結果をファイルに保存
        result_data = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": total_time,
            "api_calls": api_call_count,
            "estimated_cost": api_call_count * 0.000022,
            "personas_generated": len(personas),
            "success": total_time < 60 and len(personas) == 3
        }

        with open("test_results/small_integration_result.json", "w") as f:
            json.dump(result_data, f, indent=2)

        print("\n📄 結果を test_results/small_integration_result.json に保存しました")

        return True

    except Exception as e:
        print("\n❌ エラーが発生しました:")
        print(f"   タイプ: {type(e).__name__}")
        print(f"   詳細: {e}")

        import traceback
        traceback.print_exc()

        return False

if __name__ == "__main__":
    # 結果保存用ディレクトリ作成
    os.makedirs("test_results", exist_ok=True)

    # テスト実行
    success = asyncio.run(run_small_scale_test())

    if success:
        print("\n🎉 小規模統合テストが成功しました！")
        print("次のステップ: PersonaEvaluationAgent の実装")
    else:
        print("\n💔 テストが失敗しました。エラーを確認してください。")

    exit(0 if success else 1)
