# tests/conftest.py
"""
pytest用の共通フィクスチャとテスト設定

このファイルは全てのテストで利用可能な共通フィクスチャを定義します
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

# A2A関連のインポート（テスト実行時に利用可能）
try:
    from a2a.types import AgentCard, AgentSkill, EventQueue, TaskState
except ImportError:
    # テスト環境でa2a-sdkが利用できない場合のフォールバック
    AgentCard = AgentSkill = TaskState = EventQueue = None

from app.a2a_prototype.utils.config import AgentConfig


@pytest.fixture
def sample_agent_config():
    """テスト用のAgentConfig"""
    return AgentConfig(
        name="test-agent",
        description="Test agent for TDD",
        url="http://localhost:8001",
        port=8001,
    )


@pytest.fixture
def sample_agent_skill_data():
    """テスト用のAgentSkillデータ"""
    return {
        "id": "test_skill",
        "name": "Test Skill",
        "description": "A skill for testing",
        "tags": ["test", "unit"],
    }


@pytest.fixture
def valid_agent_skill_data():
    """有効なAgentSkillデータ（バリデーションテスト用）"""
    return {
        "id": "echo_skill",
        "name": "Echo Skill",
        "description": "Echo back user messages",
        "tags": ["text", "utility", "echo"],
    }


@pytest.fixture
def mock_event_queue():
    """EventQueueのモック"""
    if EventQueue is None:
        pytest.skip("a2a-sdk not available")

    queue = AsyncMock(spec=EventQueue)
    queue.is_closed.return_value = False
    return queue


@pytest.fixture
async def async_mock_event_queue():
    """非同期テスト用EventQueueモック"""
    if EventQueue is None:
        pytest.skip("a2a-sdk not available")

    queue = AsyncMock(spec=EventQueue)
    queue.is_closed.return_value = False

    # ライフサイクルシミュレーション
    async def mock_close():
        queue.is_closed.return_value = True

    queue.close.side_effect = mock_close
    return queue


@pytest.fixture
def mock_agent_card():
    """AgentCardのモック"""
    if AgentCard is None:
        pytest.skip("a2a-sdk not available")

    return MagicMock(spec=AgentCard)


# テストカテゴリ用マーカー
pytest_markers = [
    "unit: 単体テスト（高速・独立）",
    "integration: 統合テスト（中速・依存あり）",
    "e2e: E2Eテスト（低速・完全シナリオ）",
    "slow: 実行時間の長いテスト",
]
