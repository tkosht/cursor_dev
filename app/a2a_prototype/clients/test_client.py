#!/usr/bin/env python3
"""
A2A Test Client

A2Aエージェントとの基本的な通信をテストするクライアント
"""

import asyncio
import os
import sys
from typing import Optional

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from python_a2a import A2AClient  # noqa: E402

from app.a2a_prototype.utils.config import A2AConfig  # noqa: E402


class A2ATestClient:
    """A2Aエージェントをテストするクライアント"""

    def __init__(self):
        self.agents = {
            "weather": A2AConfig.WEATHER_AGENT,
            "calculator": A2AConfig.CALCULATOR_AGENT,
        }

    async def test_agent_card(self, agent_name: str) -> bool:
        """エージェントカードを取得してテスト"""
        if agent_name not in self.agents:
            print(f"❌ 不明なエージェント: {agent_name}")
            return False

        agent_config = self.agents[agent_name]
        print(f"🔍 Testing {agent_name} agent at {agent_config.url}")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{agent_config.url}/.well-known/agent.json"
                )

                if response.status_code == 200:
                    agent_card = response.json()
                    print("✅ エージェントカード取得成功:")
                    print(f"   名前: {agent_card.get('name', 'N/A')}")
                    print(f"   説明: {agent_card.get('description', 'N/A')}")
                    print(f"   スキル数: {len(agent_card.get('skills', []))}")
                    return True
                else:
                    print(
                        f"❌ エージェントカード取得失敗: HTTP {response.status_code}"
                    )
                    return False

        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return False

    async def send_message_to_agent(
        self, agent_name: str, message: str
    ) -> Optional[str]:
        """エージェントにメッセージを送信"""
        if agent_name not in self.agents:
            print(f"❌ 不明なエージェント: {agent_name}")
            return None

        agent_config = self.agents[agent_name]

        try:
            # A2Aクライアントを作成
            client = A2AClient(agent_config.url)

            print(f"📤 {agent_name} にメッセージ送信: '{message}'")

            # メッセージを送信（型チェック無視: python-a2aライブラリの型定義問題）
            response = await client.send_message(message)  # type: ignore

            if response:
                # レスポンスがMessage型の場合、適切に文字列に変換
                response_text = str(response) if response else "No response"
                print(f"📥 応答: {response_text}")
                return response_text
            else:
                print("❌ 応答なし")
                return None

        except Exception as e:
            print(f"❌ メッセージ送信エラー: {e}")
            return None

    async def _process_command(self, command: str) -> bool:
        """コマンドを処理する（戻り値: 継続するかどうか）"""
        parts = command.split(" ", 2)
        cmd = parts[0].lower()

        if cmd == "test" and len(parts) >= 2:
            agent_name = parts[1]
            await self.test_agent_card(agent_name)
        elif cmd == "send" and len(parts) >= 3:
            agent_name = parts[1]
            message = parts[2]
            await self.send_message_to_agent(agent_name, message)
        else:
            print(
                "❌ 不明なコマンドです。'test <agent>', 'send <agent> <message>', 'quit'"
            )

        return True

    async def run_interactive_test(self):
        """対話式テスト"""
        print("=" * 60)
        print("🤖 A2A Interactive Test Client")
        print("=" * 60)
        print()
        print("利用可能なエージェント:")
        for name, config in self.agents.items():
            print(f"  - {name}: {config.description}")
        print()
        print("コマンド:")
        print("  test <agent_name>     - エージェントのヘルスチェック")
        print("  send <agent_name> <message> - メッセージ送信")
        print("  quit                  - 終了")
        print()

        while True:
            try:
                command = input("A2A> ").strip()

                if not command:
                    continue

                if command.lower() in ["quit", "exit", "q"]:
                    break

                await self._process_command(command)
                print()  # 空行

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ エラー: {e}")

        print("\n👋 テストクライアントを終了します。")


async def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        # コマンドライン引数でのテスト
        if sys.argv[1] == "weather-test":
            client = A2ATestClient()
            await client.test_agent_card("weather")
            await client.send_message_to_agent("weather", "東京の天気を教えて")
        elif sys.argv[1] == "calculator-test":
            client = A2ATestClient()
            await client.test_agent_card("calculator")
            await client.send_message_to_agent(
                "calculator", "5 + 3 を計算して"
            )
        else:
            print(
                "使用方法: python test_client.py [weather-test|calculator-test]"
            )
    else:
        # 対話式モード
        client = A2ATestClient()
        await client.run_interactive_test()


if __name__ == "__main__":
    asyncio.run(main())
