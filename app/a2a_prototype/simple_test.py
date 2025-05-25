#!/usr/bin/env python3
"""
最小限のA2A-SDK動作確認テスト

Google公式a2a-sdk v0.2.4の基本的な型とインポートが正しく動作するかテストする

【使用方法】
cd /home/devuser/workspace
python app/a2a_prototype/simple_test.py

【期待される出力】
✅ A2A SDK imports successful
✅ AgentCard created successfully
✅ TaskState values (submitted, working, etc.)
✅ EventQueue created and managed successfully

【このテストの目的】
1. a2a-sdkの基本的なインポートが成功するか確認
2. AgentCardオブジェクトの作成が正常に動作するか確認
3. TaskState列挙型の各値にアクセスできるか確認
4. EventQueueの基本的な作成・クローズ操作が動作するか確認

【前提条件】
- Python 3.10+
- a2a-sdk v0.2.4がインストール済み
- Poetry環境が有効
"""

import asyncio
import logging

print("A2A SDK Basic Test Suite")
print("=" * 50)
print("Testing Google official a2a-sdk v0.2.4...")

# A2A SDK インポートテスト
try:
    from a2a.server.events.event_queue import EventQueue
    from a2a.types import AgentCard, AgentSkill, TaskState
    print("✅ A2A SDK imports successful")
    print("   - EventQueue: Event handling for asynchronous agent communication")  
    print("   - AgentCard: Agent metadata and capability description")
    print("   - AgentSkill: Individual agent capabilities definition")
    print("   - TaskState: Task lifecycle state management")
except ImportError as e:
    print(f"❌ A2A SDK import failed: {e}")
    print("解決方法:")
    print("1. a2a-sdkがインストールされているか確認: poetry show a2a-sdk")
    print("2. 仮想環境がアクティブになっているか確認")
    print("3. 依存関係を再インストール: poetry install")
    exit(1)


def test_agent_card_creation():
    """AgentCardの作成テスト"""
    print("\n=== Testing AgentCard Creation ===")
    
    try:
        # シンプルなスキルを作成
        skill = AgentSkill(
            id="test-skill",
            name="Test Skill",
            description="A simple test skill",
            tags=["test"]
        )
        
        # AgentCardを作成
        agent_card = AgentCard(
            name="test-agent",
            description="A simple test agent",
            url="http://localhost:8001",
            version="1.0.0",
            capabilities={},  # AgentCapabilitiesの詳細は後で
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=[skill]
        )
        
        print("✅ AgentCard created successfully:")
        print(f"   Name: {agent_card.name}")
        print(f"   Description: {agent_card.description}")
        print(f"   URL: {agent_card.url}")
        print(f"   Skills: {len(agent_card.skills)}")
        
        return agent_card
        
    except Exception as e:
        print(f"❌ AgentCard creation failed: {e}")
        return None


def test_task_state():
    """TaskState列挙型のテスト"""
    print("\n=== Testing TaskState ===")
    
    try:
        states = [
            TaskState.submitted,
            TaskState.working,
            TaskState.input_required,
            TaskState.completed,
            TaskState.canceled,
            TaskState.failed
        ]
        
        print("✅ TaskState values:")
        for state in states:
            print(f"   - {state.name}: {state.value}")
            
    except Exception as e:
        print(f"❌ TaskState test failed: {e}")


async def test_event_queue():
    """EventQueueの基本動作テスト"""
    print("\n=== Testing EventQueue ===")
    
    try:
        # EventQueueを作成
        queue = EventQueue()
        
        print("✅ EventQueue created successfully")
        print(f"   Queue closed: {queue.is_closed()}")
        
        # クローズテスト
        await queue.close()
        print(f"   Queue closed after close(): {queue.is_closed()}")
        
    except Exception as e:
        print(f"❌ EventQueue test failed: {e}")


async def main():
    """メインテスト関数"""
    print("A2A SDK Basic Test Suite")
    print("=" * 50)
    
    # 基本テスト
    test_agent_card_creation()
    test_task_state()
    await test_event_queue()
    
    print("\n" + "=" * 50)
    print("Basic tests completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 