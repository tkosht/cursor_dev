#!/usr/bin/env python3
"""
Simple A2A Agent Demo Script

SimpleTestAgentの動作確認・デモ用スクリプト

【このファイルの位置づけ】
- 手動実行による動作確認用スクリプト（pytest テストではない）
- SimpleTestAgentの機能をインタラクティブに確認
- 開発中の動作確認やデバッグに使用

【真のpytestテスト】
- tests/unit/test_agents/test_simple_agent.py で TDD実践版を参照

【使用方法】
cd /home/devuser/workspace
python examples/simple_agent_demo.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path


def setup_project_path():
    """プロジェクトパスを設定し、必要なモジュールをインポート"""
    # プロジェクトルートをPythonパスに追加
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 動的インポート
    from app.a2a_prototype.agents.simple_agent import create_test_agent
    return create_test_agent


async def test_agent_card(create_test_agent):
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


async def test_process_user_input(create_test_agent):
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


def test_agent_config(create_test_agent):
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
    
    print("A2A Simple Agent Demo")
    print("=" * 50)
    print("※ これは動作確認用デモスクリプトです")
    print("※ TDD準拠のpytestテストは tests/unit/test_agents/test_simple_agent.py を参照")
    print("=" * 50)
    
    try:
        # 一度だけプロジェクトパスを設定し、create_test_agent関数を取得
        create_test_agent = setup_project_path()
        
        # 基本的なテストを実行
        test_agent_config(create_test_agent)
        await test_agent_card(create_test_agent)
        await test_process_user_input(create_test_agent)
        
        print("\n" + "=" * 50)
        print("✅ All demo tests completed successfully!")
        print("\n📝 次のステップ:")
        print("1. poetry run pytest tests/unit/ でTDD準拠のテストを実行")
        print("2. poetry run pytest tests/ --cov=src で包括的テスト実行")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 