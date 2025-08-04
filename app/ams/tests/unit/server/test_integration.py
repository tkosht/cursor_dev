"""
Integration tests for FastAPI server with OrchestratorAgent
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.core.types import SimulationConfig, SimulationStatus
from src.server.app import app


@pytest.fixture
def test_client():
    """Create test client with lifespan events"""
    with TestClient(app) as client:
        yield client


class TestOrchestratorIntegration:
    """Test orchestrator integration with FastAPI server"""

    @patch("src.server.simulation_service.OrchestratorAgent")
    def test_simulation_with_orchestrator_mock(self, mock_orchestrator_class, test_client):
        """Test simulation creation triggers orchestrator (with mocked orchestrator)"""
        # Setup mock orchestrator
        mock_orchestrator = MagicMock()
        mock_graph = MagicMock()
        
        # Make astream return an async generator
        async def mock_astream(*args, **kwargs):
            yield {"orchestrator": {"current_phase": "initialization"}}
            yield {"orchestrator": {"current_phase": "completed"}}
        
        # Make aget_state return a mock state
        async def mock_aget_state(*args, **kwargs):
            mock_state = MagicMock()
            mock_state.values = {
                "persona_evaluations": [],
                "aggregation_results": {
                    "overall_relevance": 0.8,
                    "overall_quality": 0.9,
                    "overall_engagement": 0.7,
                    "market_segments": [],
                    "key_insights": ["Test insight"],
                    "recommendations": ["Test recommendation"],
                },
                "persona_count": 10,
                "start_time": None,
                "end_time": None,
            }
            return mock_state
        
        mock_graph.astream = mock_astream
        mock_graph.aget_state = mock_aget_state
        mock_orchestrator.compile.return_value = mock_graph
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Create simulation
        response = test_client.post(
            "/api/simulations",
            json={
                "article_content": "Test article content",
                "article_metadata": {"title": "Test Article"},
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        
        # Give background task time to start
        # In a real test, we'd wait for the status to change
        # But for unit tests, we just verify the orchestrator was called
        assert mock_orchestrator_class.called
        assert mock_orchestrator.compile.called

    def test_simulation_status_tracking(self, test_client):
        """Test simulation status can be tracked"""
        # Create simulation
        create_response = test_client.post(
            "/api/simulations",
            json={
                "article_content": "Test article for status tracking",
                "article_metadata": {"title": "Status Test"},
            }
        )
        
        assert create_response.status_code == 201
        simulation_id = create_response.json()["id"]
        
        # Check status
        status_response = test_client.get(f"/api/simulations/{simulation_id}/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["id"] == simulation_id
        assert "status" in status_data
        assert "progress" in status_data
        assert status_data["progress"] >= 0.0 and status_data["progress"] <= 1.0

    def test_simulation_with_custom_config(self, test_client):
        """Test simulation creation with custom configuration"""
        custom_config = {
            "num_personas": 25,
            "diversity_level": 0.8,
            "analysis_depth": "deep",
            "llm_provider": "openai",
            "parallel_processing": False,
        }
        
        response = test_client.post(
            "/api/simulations",
            json={
                "article_content": "Article with custom config",
                "article_metadata": {"title": "Custom Config Test"},
                "config": custom_config,
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify simulation was created
        simulation_id = data["id"]
        get_response = test_client.get(f"/api/simulations/{simulation_id}")
        assert get_response.status_code == 200

    @pytest.mark.asyncio
    async def test_websocket_updates_during_simulation(self, test_client):
        """Test WebSocket receives updates during simulation"""
        # Create simulation first
        create_response = test_client.post(
            "/api/simulations",
            json={
                "article_content": "WebSocket test article",
                "article_metadata": {"title": "WebSocket Test"},
            }
        )
        
        simulation_id = create_response.json()["id"]
        
        # Connect to WebSocket
        with test_client.websocket_connect(f"/ws/simulations/{simulation_id}") as websocket:
            # Should receive initial status
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert "data" in data
            assert "status" in data["data"]
            assert "progress" in data["data"]