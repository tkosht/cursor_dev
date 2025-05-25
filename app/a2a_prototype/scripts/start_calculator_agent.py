#!/usr/bin/env python3
"""
Calculator Agent Starter

Calculator Agentを個別に起動するスクリプト
"""

import os
import sys

# パスを追加してインポートを可能にする
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from app.a2a_prototype.agents.calculator_agent import CalculatorAgent


def main():
    """Calculator Agentを起動"""
    print("=" * 50)
    print("🧮 Calculator Agent Starting...")
    print("=" * 50)
    
    try:
        agent = CalculatorAgent()
        print(f"Agent URL: {agent.config.url}")
        print(f"Agent Card available at: {agent.config.url}/.well-known/agent.json")
        print()
        print("エージェントが起動しました。停止するには Ctrl+C を押してください。")
        print()
        
        # エージェント起動
        agent.run_agent()
        
    except KeyboardInterrupt:
        print("\n👋 Calculator Agent を停止しています...")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 