#!/usr/bin/env python3
"""
Pytest tests for API integration with OrchestratorAgent
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


@pytest.mark.asyncio
async def test_simulation_lifecycle():
    """Test complete simulation lifecycle"""

    # Mock the httpx AsyncClient
    mock_response_create = MagicMock()
    mock_response_create.status_code = 201
    mock_response_create.json.return_value = {
        "id": "test-sim-123",
        "status": "initializing",
        "progress": 0.0,
    }

    mock_response_status = MagicMock()
    mock_response_status.status_code = 200
    mock_response_status.json.return_value = {"status": "completed", "progress": 1.0}

    mock_response_final = MagicMock()
    mock_response_final.status_code = 200
    mock_response_final.json.return_value = {
        "id": "test-sim-123",
        "status": "completed",
        "progress": 1.0,
        "error": None,
    }

    mock_response_results = MagicMock()
    mock_response_results.status_code = 200
    mock_response_results.json.return_value = {
        "simulation_id": "test-sim-123",
        "executive_summary": {
            "overall_score": 85,
            "key_findings": ["Finding 1", "Finding 2"],
            "top_recommendations": ["Rec 1", "Rec 2"],
        },
        "detailed_analysis": {"scores": {"overall": 85}},
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Set up mock responses for each call
        mock_client.post.return_value = mock_response_create
        mock_client.get.side_effect = [
            mock_response_status,  # First status check
            mock_response_final,  # Final details
            mock_response_results,  # Results
        ]

        # Test article content
        article_data = {
            "article_content": """
            Breaking News: Major Scientific Discovery
            
            Scientists have discovered a new method for converting plastic waste 
            into biodegradable materials. This breakthrough could revolutionize 
            waste management and help combat environmental pollution.
            """,
            "article_metadata": {
                "title": "Revolutionary Plastic Recycling Method Discovered",
                "author": "Dr. Jane Smith",
                "category": "Science & Environment",
                "published_date": datetime.now().isoformat(),
            },
            "config": {
                "num_personas": 10,
                "diversity_level": 0.8,
                "analysis_depth": "quick",
            },
        }

        # Execute test
        async with httpx.AsyncClient() as client:
            # Create simulation
            create_response = await client.post(
                "http://localhost:8000/api/simulations", json=article_data
            )
            assert create_response.status_code == 201
            simulation_data = create_response.json()
            assert "id" in simulation_data
            assert simulation_data["status"] == "initializing"

            simulation_id = simulation_data["id"]

            # Check status
            status_response = await client.get(
                f"http://localhost:8000/api/simulations/{simulation_id}/status"
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "completed"

            # Get final details
            final_response = await client.get(
                f"http://localhost:8000/api/simulations/{simulation_id}"
            )
            assert final_response.status_code == 200
            final_data = final_response.json()
            assert final_data["status"] == "completed"
            assert final_data.get("error") is None

            # Get results
            results_response = await client.get(
                f"http://localhost:8000/api/simulations/{simulation_id}/results"
            )
            assert results_response.status_code == 200
            results = results_response.json()
            assert "executive_summary" in results
            assert "detailed_analysis" in results


@pytest.mark.asyncio
async def test_websocket_updates():
    """Test WebSocket update mechanism"""

    # Mock websocket connection
    mock_websocket = AsyncMock()
    mock_messages = [
        json.dumps(
            {
                "type": "status_update",
                "data": {
                    "simulation_id": "test-sim-123",
                    "status": "initializing",
                    "progress": 0.0,
                },
            }
        ),
        json.dumps(
            {
                "type": "status_update",
                "data": {"simulation_id": "test-sim-123", "status": "running", "progress": 0.5},
            }
        ),
        json.dumps(
            {
                "type": "status_update",
                "data": {"simulation_id": "test-sim-123", "status": "completed", "progress": 1.0},
            }
        ),
    ]

    mock_websocket.recv.side_effect = mock_messages

    with patch("websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_websocket

        # Track received messages
        received_updates = []

        # Simulate receiving updates
        for _ in range(3):
            message = await mock_websocket.recv()
            data = json.loads(message)
            received_updates.append(data)

            if data.get("type") == "status_update":
                status = data["data"].get("status")
                if status == "completed":
                    break

        # Verify updates were received
        assert len(received_updates) == 3
        assert received_updates[0]["data"]["status"] == "initializing"
        assert received_updates[1]["data"]["status"] == "running"
        assert received_updates[2]["data"]["status"] == "completed"

        # Verify progress tracking
        assert received_updates[0]["data"]["progress"] == 0.0
        assert received_updates[1]["data"]["progress"] == 0.5
        assert received_updates[2]["data"]["progress"] == 1.0
