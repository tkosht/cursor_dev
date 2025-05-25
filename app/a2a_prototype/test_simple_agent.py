#!/usr/bin/env python3
"""
Simple A2A Agent Test Script

SimpleTestAgentの基本動作確認用スクリプト
"""

import asyncio
import json
import logging

from app.a2a_prototype.agents.simple_agent import create_test_agent


async def test_agent_card():
    """エージェントカードの基本テスト"""
    print("=== Testing Agent Card ===")
    
    # テストエージェントを作成
    agent = create_test_agent(8001)
    
    # エージェントカードの内容を確認
    card = agent.agent_card
    
    print(f"Agent Name: {card.name}")
    print(f"Description: {card.description}")
    print(f"URL: {card.url}")
    print(f"Version: {card.version}")
    print(f"Capabilities: {card.capabilities}")
    print(f"Input Modes: {card.defaultInputModes}")
    print(f"Output Modes: {card.defaultOutputModes}")
    
    print("\nSkills:")
    for skill in card.skills:
        print(f"  - {skill.name}: {skill.description}")
    
    print("\nAgent Card JSON representation:")
    try:
        # Agent Cardをdict形式で表示
        card_dict = card.model_dump() if hasattr(card, 'model_dump') else card.__dict__
        print(json.dumps(card_dict, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Failed to serialize agent card: {e}")
        print(f"Agent card object: {card}")


async def test_process_user_input():
    """ユーザー入力処理のテスト"""
    print("\n=== Testing User Input Processing ===")
    
    agent = create_test_agent(8001)
    
    test_inputs = [
        "hello",
        "hi there",
        "echo test message",
        "status",
        "help",
        "random input"
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: '{input_text}'")
        try:
            response = await agent.process_user_input(input_text)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error processing input: {e}")


def test_agent_config():
    """エージェント設定のテスト"""
    print("\n=== Testing Agent Configuration ===")
    
    agent = create_test_agent(8001)
    config = agent.config
    
    print(f"Config Name: {config.name}")
    print(f"Config Description: {config.description}")
    print(f"Config URL: {config.url}")
    print(f"Config Port: {config.port}")
    print(f"Config Version: {config.version}")


async def main():
    """メインテスト関数"""
    logging.basicConfig(level=logging.INFO)
    
    print("A2A Simple Agent Test Suite")
    print("=" * 50)
    
    try:
        # 基本的なテストを実行
        test_agent_config()
        await test_agent_card()
        await test_process_user_input()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 