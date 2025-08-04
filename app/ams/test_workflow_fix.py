#!/usr/bin/env python3
"""Test case for verifying the workflow fix"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_workflow_transitions():
    """Test that workflow transitions work correctly"""
    from src.agents.orchestrator import OrchestratorAgent
    from src.core.types import SimulationConfig
    
    logger.info("=== Testing Workflow Transitions ===")
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    graph = orchestrator.compile()
    
    # Test initial state
    initial_state = {
        "article_content": "Test article for workflow validation",
        "article_metadata": {"title": "Test", "author": "System"},
        "current_phase": "initialization",
        "phase_status": {},
        "active_agents": [],
        "agent_status": {},
        "analysis_results": {},
        "persona_count": 10,
        "generated_personas": [],
        "persona_generation_complete": False,
        "persona_evaluations": {},
        "evaluation_complete": False,
        "aggregated_scores": {},
        "improvement_suggestions": [],
        "final_report": {},
        "errors": [],
        "messages": [],
        "retry_count": {},
        "simulation_id": "test_001",
        "start_time": datetime.now(),
        "end_time": None,
    }
    
    # Expected phase transitions
    # Note: The workflow goes directly from aggregation to completed after reporter runs
    # because the orchestrator checks for final_report before phase-specific logic
    expected_transitions = [
        ("initialization", "analysis"),
        ("analysis", "persona_generation"),
        ("persona_generation", "evaluation"),
        ("evaluation", "aggregation"),
        ("aggregation", "completed")  # Reporter runs but phase goes directly to completed
    ]
    
    logger.info("Starting workflow execution...")
    
    # Track actual transitions
    actual_transitions = []
    previous_phase = "initialization"
    
    try:
        # Run workflow and collect phase transitions
        config = {"configurable": {"thread_id": "test_001"}}
        async for chunk in graph.astream(initial_state, config=config):
            # Log chunk keys
            logger.info(f"Chunk keys: {list(chunk.keys())}")
            
            # Extract current phase from any node update
            current_phase = None
            for node_name, node_state in chunk.items():
                if isinstance(node_state, dict) and "current_phase" in node_state:
                    current_phase = node_state["current_phase"]
                    break
            
            if current_phase and current_phase != previous_phase:
                actual_transitions.append((previous_phase, current_phase))
                logger.info(f"Phase transition: {previous_phase} → {current_phase}")
                previous_phase = current_phase
                
                # Stop if we reach completed
                if current_phase == "completed":
                    break
                    
            # Check if workflow reached completion state
            if previous_phase == "reporting" and not any(t[1] == "completed" for t in actual_transitions):
                # The workflow might have ended without a final transition
                # Check the final state
                final_chunk = chunk
                for node_name, node_state in final_chunk.items():
                    if isinstance(node_state, dict) and node_state.get("current_phase") == "completed":
                        actual_transitions.append((previous_phase, "completed"))
                        break
        
        # Compare expected vs actual
        logger.info("\n=== Transition Validation ===")
        logger.info(f"Expected transitions: {expected_transitions}")
        logger.info(f"Actual transitions: {actual_transitions}")
        
        # Check if all expected transitions occurred
        success = True
        for expected in expected_transitions:
            if expected not in actual_transitions:
                logger.error(f"Missing transition: {expected[0]} → {expected[1]}")
                success = False
        
        if success:
            logger.info("✅ All expected transitions completed successfully!")
        else:
            logger.error("❌ Some transitions failed!")
            
        return success
        
    except Exception as e:
        logger.error(f"Error during workflow execution: {e}", exc_info=True)
        return False

async def test_simulation_completion():
    """Test full simulation completion"""
    from src.server.simulation_service import SimulationService
    from src.server.app_types import SimulationData
    from src.core.types import SimulationStatus, SimulationConfig
    
    logger.info("\n=== Testing Full Simulation Completion ===")
    
    # Create test simulation
    test_id = "test_completion_001"
    simulations = {
        test_id: SimulationData(
            id=test_id,
            status=SimulationStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            progress=0.0,
            article_content="Test article for completion verification",
            article_metadata={"title": "Completion Test"},
            config=SimulationConfig(num_personas=10),
            result=None,
            error=None,
        )
    }
    
    # Create service
    service = SimulationService(simulations)
    
    # Run simulation
    logger.info(f"Starting simulation {test_id}")
    
    try:
        await service.run_simulation(test_id)
        
        # Check final state
        final_status = simulations[test_id]["status"]
        final_progress = simulations[test_id]["progress"]
        
        logger.info(f"Final status: {final_status}")
        logger.info(f"Final progress: {final_progress}")
        
        if final_status == SimulationStatus.COMPLETED and final_progress == 1.0:
            logger.info("✅ Simulation completed successfully!")
            return True
        else:
            logger.error("❌ Simulation did not complete properly!")
            return False
            
    except Exception as e:
        logger.error(f"Error during simulation: {e}", exc_info=True)
        return False

async def main():
    """Run all tests"""
    logger.info("Starting workflow fix validation tests...")
    
    # Test 1: Workflow transitions
    test1_result = await test_workflow_transitions()
    
    # Test 2: Full simulation completion
    test2_result = await test_simulation_completion()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Workflow transitions: {'PASS' if test1_result else 'FAIL'}")
    logger.info(f"Simulation completion: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        logger.info("\n✅ All tests passed! Workflow fix is successful.")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Fix needs more work.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)