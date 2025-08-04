#!/usr/bin/env python3
"""
Manual test script for API integration with OrchestratorAgent
"""

import asyncio
import json
import time
from datetime import datetime

import httpx


async def test_simulation_lifecycle():
    """Test complete simulation lifecycle"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. Create simulation
        print("Creating simulation...")
        create_response = await client.post(
            f"{base_url}/api/simulations",
            json={
                "article_content": """
                Breaking News: Major Scientific Discovery
                
                Scientists have discovered a new method for converting plastic waste 
                into biodegradable materials. This breakthrough could revolutionize 
                waste management and help combat environmental pollution.
                
                The new process uses a combination of enzymes and heat treatment
                to break down plastic polymers into organic compounds that can
                be safely absorbed by the environment.
                """,
                "article_metadata": {
                    "title": "Revolutionary Plastic Recycling Method Discovered",
                    "author": "Dr. Jane Smith",
                    "category": "Science & Environment",
                    "published_date": datetime.now().isoformat(),
                },
                "config": {
                    "num_personas": 10,  # Small number for quick test
                    "diversity_level": 0.8,
                    "analysis_depth": "quick",
                }
            }
        )
        
        if create_response.status_code != 201:
            print(f"Failed to create simulation: {create_response.text}")
            return
            
        simulation_data = create_response.json()
        simulation_id = simulation_data["id"]
        print(f"Created simulation: {simulation_id}")
        print(f"Initial status: {simulation_data['status']}")
        
        # 2. Poll status until completion
        print("\nPolling simulation status...")
        max_polls = 60  # Maximum 5 minutes
        poll_interval = 5  # Check every 5 seconds
        
        for i in range(max_polls):
            status_response = await client.get(
                f"{base_url}/api/simulations/{simulation_id}/status"
            )
            
            if status_response.status_code != 200:
                print(f"Failed to get status: {status_response.text}")
                break
                
            status_data = status_response.json()
            print(f"[{i+1}] Status: {status_data['status']}, Progress: {status_data['progress']:.2%}")
            
            if status_data["status"] in ["completed", "failed", "cancelled"]:
                break
                
            await asyncio.sleep(poll_interval)
        
        # 3. Get full simulation details
        print("\nGetting final simulation details...")
        final_response = await client.get(
            f"{base_url}/api/simulations/{simulation_id}"
        )
        
        if final_response.status_code != 200:
            print(f"Failed to get simulation: {final_response.text}")
            return
            
        final_data = final_response.json()
        print(f"Final status: {final_data['status']}")
        print(f"Progress: {final_data['progress']:.2%}")
        
        if final_data.get("error"):
            print(f"Error: {final_data['error']}")
        
        # 4. Get results if completed
        if final_data["status"] == "completed":
            print("\nGetting simulation results...")
            results_response = await client.get(
                f"{base_url}/api/simulations/{simulation_id}/results"
            )
            
            if results_response.status_code == 200:
                results = results_response.json()
                print(f"Simulation completed successfully!")
                print(f"Result available: {results['id']}")
                # Pretty print a subset of results
                if "result" in results and results["result"]:
                    result_data = results["result"]
                    print(f"\nSummary:")
                    print(f"- Total personas evaluated: {result_data.get('total_personas', 0)}")
                    print(f"- Overall relevance: {result_data.get('overall_relevance', 0):.2%}")
                    print(f"- Overall quality: {result_data.get('overall_quality', 0):.2%}")
                    print(f"- Overall engagement: {result_data.get('overall_engagement', 0):.2%}")
                    print(f"- Processing time: {result_data.get('processing_time_seconds', 0):.2f}s")
            else:
                print(f"Failed to get results: {results_response.text}")


async def test_websocket_updates():
    """Test WebSocket real-time updates"""
    import websockets
    
    base_url = "http://localhost:8000"
    ws_url = "ws://localhost:8000"
    
    # First create a simulation
    async with httpx.AsyncClient() as client:
        create_response = await client.post(
            f"{base_url}/api/simulations",
            json={
                "article_content": "Test article for WebSocket updates",
                "article_metadata": {"title": "WebSocket Test"},
                "config": {"num_personas": 5}
            }
        )
        
        simulation_id = create_response.json()["id"]
        print(f"Created simulation: {simulation_id}")
    
    # Connect to WebSocket
    print("\nConnecting to WebSocket...")
    async with websockets.connect(f"{ws_url}/ws/simulations/{simulation_id}") as websocket:
        print("Connected! Waiting for updates...")
        
        # Listen for updates
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(message)
                print(f"WebSocket update: {data}")
                
                # Check if simulation is complete
                if data.get("type") == "status_update":
                    status = data["data"].get("status")
                    if status in ["completed", "failed", "cancelled"]:
                        print(f"Simulation {status}")
                        break
                        
        except asyncio.TimeoutError:
            print("No updates received for 30 seconds")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("AMS API Integration Test")
    print("=" * 60)
    
    print("\nMake sure the API server is running:")
    print("  poetry run uvicorn src.server.app:app --reload")
    print("\nPress Enter to continue...")
    input()
    
    # Test basic lifecycle
    print("\n### Testing Simulation Lifecycle ###")
    await test_simulation_lifecycle()
    
    # Test WebSocket (optional)
    print("\n\n### Testing WebSocket Updates ###")
    try:
        await test_websocket_updates()
    except Exception as e:
        print(f"WebSocket test failed: {e}")
    
    print("\n\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())