"""
Gemini A2A Agent 実行スクリプト

Google Gemini 2.5 Pro統合A2Aエージェントを起動
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_logging() -> None:
    """ログ設定をセットアップ"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("gemini_agent.log"),
        ],
    )


async def main() -> None:
    """Geminiエージェントを起動"""
    # ローカルインポート（パス設定後）
    from app.a2a_prototype.agents import create_gemini_agent

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 環境変数確認
        if not os.getenv("GEMINI_API_KEY"):
            print("❌ GEMINI_API_KEY environment variable is required")
            print()
            print("🔧 **Setting up API Key:**")
            print("   1. Get your API key: https://makersuite.google.com/app/apikey")
            print("   2. Create .env file: cp .env.example .env")
            print("   3. Edit .env file and set: GEMINI_API_KEY=your-actual-api-key")
            print("   4. Or export: export GEMINI_API_KEY='your-actual-api-key'")
            print()
            print("📖 Detailed guide: docs/setup/api_key_configuration.md")
            print("💡 Note: .env file is Git-ignored for security")
            return

        # Geminiエージェント作成
        agent = create_gemini_agent(port=8004)

        print(f"🚀 Starting {agent.config.name}...")
        print(f"📡 URL: {agent.config.url}")
        print(f"🧠 Model: {agent.gemini_config.model}")
        print(f"🌡️ Temperature: {agent.gemini_config.temperature}")
        print(f"💡 Test at: {agent.config.url}/.well-known/agent.json")
        print(f"📊 Health check: {agent.config.url}/health")
        print("\n💬 Ready for A2A conversations!")

        # ヘルスチェック実行
        health = await agent.gemini_client.health_check()
        if health:
            print("✅ Gemini API connection verified")
        else:
            print("⚠️ Warning: Gemini API health check failed")

        # エージェント起動
        agent.run_agent(host="0.0.0.0", port=8004)

    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user.")
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
