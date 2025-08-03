"""
Tests for FastAPI server application
"""

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.core.types import SimulationStatus
from src.server.app import app, simulations


@pytest.fixture
def test_client():
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_simulations():
    """Clear simulations between tests"""
    simulations.clear()
    yield
    simulations.clear()


class TestHealthCheck:
    """Health check endpoint tests"""

    def test_health_check_returns_healthy(self, test_client):
        """ヘルスチェックが正常に動作することを確認"""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "0.1.0"


class TestSimulationCreate:
    """Simulation creation endpoint tests"""

    def test_create_simulation_minimal(self, test_client):
        """最小限のパラメータでシミュレーション作成"""
        request_data = {"article_content": "This is a test article about AI and technology."}

        response = test_client.post("/api/simulations", json=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["status"] == SimulationStatus.PENDING.value
        assert data["progress"] == 0.0
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_simulation_with_metadata(self, test_client):
        """メタデータ付きでシミュレーション作成"""
        request_data = {
            "article_content": "This is a test article about AI and technology.",
            "article_metadata": {
                "title": "AI Revolution",
                "author": "Test Author",
                "category": "Technology",
            },
        }

        response = test_client.post("/api/simulations", json=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data

        # Check stored data
        sim_id = data["id"]
        assert sim_id in simulations
        assert simulations[sim_id]["article_metadata"]["title"] == "AI Revolution"

    def test_create_simulation_with_config(self, test_client):
        """カスタム設定でシミュレーション作成"""
        request_data = {
            "article_content": "This is a test article about AI and technology.",
            "config": {"num_personas": 100, "diversity_level": 0.9, "analysis_depth": "deep"},
        }

        response = test_client.post("/api/simulations", json=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data

        # Check stored config
        sim_id = data["id"]
        config = simulations[sim_id]["config"]
        assert config.num_personas == 100
        assert config.diversity_level == 0.9
        assert config.analysis_depth == "deep"

    def test_create_simulation_invalid_data(self, test_client):
        """無効なデータでのシミュレーション作成エラー"""
        request_data = {
            # article_content is missing
            "article_metadata": {"title": "Test"}
        }

        response = test_client.post("/api/simulations", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSimulationGet:
    """Simulation retrieval endpoint tests"""

    def test_get_simulation_success(self, test_client):
        """存在するシミュレーションの取得"""
        # Create a simulation first
        sim_id = str(uuid.uuid4())
        simulations[sim_id] = {
            "id": sim_id,
            "status": SimulationStatus.RUNNING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "progress": 0.5,
            "result": None,
            "error": None,
        }

        response = test_client.get(f"/api/simulations/{sim_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sim_id
        assert data["status"] == SimulationStatus.RUNNING.value
        assert data["progress"] == 0.5

    def test_get_simulation_not_found(self, test_client):
        """存在しないシミュレーションの取得エラー"""
        fake_id = str(uuid.uuid4())

        response = test_client.get(f"/api/simulations/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data


class TestSimulationStatus:
    """Simulation status endpoint tests"""

    def test_get_status_success(self, test_client):
        """シミュレーションステータスの取得"""
        # Create a simulation
        sim_id = str(uuid.uuid4())
        simulations[sim_id] = {
            "id": sim_id,
            "status": SimulationStatus.RUNNING,
            "progress": 0.75,
            "updated_at": datetime.utcnow(),
        }

        response = test_client.get(f"/api/simulations/{sim_id}/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sim_id
        assert data["status"] == SimulationStatus.RUNNING.value
        assert data["progress"] == 0.75
        assert "updated_at" in data

    def test_get_status_not_found(self, test_client):
        """存在しないシミュレーションのステータス取得エラー"""
        fake_id = str(uuid.uuid4())

        response = test_client.get(f"/api/simulations/{fake_id}/status")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSimulationResults:
    """Simulation results endpoint tests"""

    def test_get_results_completed(self, test_client):
        """完了したシミュレーションの結果取得"""
        # Create a completed simulation
        sim_id = str(uuid.uuid4())
        mock_result = {
            "simulation_id": sim_id,
            "total_personas": 50,
            "overall_relevance": 0.85,
            "overall_quality": 0.78,
            "overall_engagement": 0.82,
        }

        simulations[sim_id] = {
            "id": sim_id,
            "status": SimulationStatus.COMPLETED,
            "result": mock_result,
            "updated_at": datetime.utcnow(),
        }

        response = test_client.get(f"/api/simulations/{sim_id}/results")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sim_id
        assert data["result"]["total_personas"] == 50
        assert data["result"]["overall_relevance"] == 0.85

    def test_get_results_not_completed(self, test_client):
        """未完了シミュレーションの結果取得エラー"""
        # Create a running simulation
        sim_id = str(uuid.uuid4())
        simulations[sim_id] = {"id": sim_id, "status": SimulationStatus.RUNNING, "result": None}

        response = test_client.get(f"/api/simulations/{sim_id}/results")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "not completed" in data["error"]

    def test_get_results_not_found(self, test_client):
        """存在しないシミュレーションの結果取得エラー"""
        fake_id = str(uuid.uuid4())

        response = test_client.get(f"/api/simulations/{fake_id}/results")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestWebSocket:
    """WebSocket endpoint tests"""

    def test_websocket_connection_valid_simulation(self, test_client):
        """有効なシミュレーションIDでのWebSocket接続"""
        # Create a simulation
        sim_id = str(uuid.uuid4())
        simulations[sim_id] = {"id": sim_id, "status": SimulationStatus.RUNNING, "progress": 0.0}

        with test_client.websocket_connect(f"/ws/simulations/{sim_id}") as websocket:
            # Should receive initial status
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["data"]["status"] == SimulationStatus.RUNNING.value
            assert data["data"]["progress"] == 0.0

    def test_websocket_connection_invalid_simulation(self, test_client):
        """無効なシミュレーションIDでのWebSocket接続エラー"""
        fake_id = str(uuid.uuid4())

        with pytest.raises(Exception):  # WebSocket should close immediately
            with test_client.websocket_connect(f"/ws/simulations/{fake_id}") as websocket:
                pass


class TestErrorHandlers:
    """Error handler tests"""

    def test_http_exception_handler(self, test_client):
        """HTTPException handler が正しく動作することを確認"""
        response = test_client.get("/api/simulations/invalid-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "status_code" in data
        assert "timestamp" in data

    @patch("src.server.app.simulations", side_effect=Exception("Test error"))
    def test_general_exception_handler(self, mock_simulations, test_client):
        """一般的な例外ハンドラーが正しく動作することを確認"""
        response = test_client.get("/api/simulations/any-id")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["error"] == "Internal server error"
        assert data["status_code"] == 500
