"""
Simulation service for background processing
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from ..agents.orchestrator import ArticleReviewState, OrchestratorAgent
from ..core.types import SimulationConfig, SimulationResult, SimulationStatus
from .app_types import SimulationData

logger = logging.getLogger(__name__)


class SimulationService:
    """Service for running simulations in the background"""

    def __init__(self, simulations_store: dict[str, SimulationData], manager: Any = None) -> None:
        self.simulations = simulations_store
        self.orchestrator = OrchestratorAgent()
        self.graph = self.orchestrator.compile()
        self.manager = manager  # WebSocket connection manager

    async def run_simulation(self, simulation_id: str) -> None:
        """Run a simulation asynchronously"""
        logger.info(f"Starting simulation {simulation_id}")
        try:
            simulation = self.simulations[simulation_id]
            
            # Update status to initializing
            await self._update_status(simulation_id, SimulationStatus.INITIALIZING, 0.1)
            
            # Prepare initial state for orchestrator
            initial_state: ArticleReviewState = {
                "article_content": simulation["article_content"],
                "article_metadata": simulation["article_metadata"],
                "current_phase": "initialization",
                "phase_status": {},
                "active_agents": [],
                "agent_status": {},
                "analysis_results": {},
                "persona_count": simulation["config"].num_personas,
                "generated_personas": [],
                "persona_generation_complete": False,
                "persona_evaluations": {},  # Changed from list to dict
                "evaluation_complete": False,  # Added missing field
                "aggregated_scores": {},  # Added missing field
                "improvement_suggestions": [],  # Added missing field
                "final_report": {},  # Changed from str to dict
                "errors": [],
                "messages": [],
                "retry_count": {},  # Added missing field
                "simulation_id": simulation_id,  # Added missing field
                "start_time": datetime.now(),
                "end_time": None,
            }
            
            logger.info(f"Initial state prepared for simulation {simulation_id}")
            
            # Update status to running
            await self._update_status(simulation_id, SimulationStatus.RUNNING, 0.2)
            
            # Run the orchestrator workflow
            logger.info(f"Starting workflow execution for simulation {simulation_id}")
            chunk_count = 0
            async for chunk in self.graph.astream(
                initial_state, 
                config={"configurable": {"thread_id": simulation_id}}
            ):
                chunk_count += 1
                logger.info(f"Processing chunk {chunk_count} for simulation {simulation_id}: {list(chunk.keys())}")
                # Process updates from the workflow
                await self._process_workflow_update(simulation_id, chunk)
            
            # Get final state
            final_state = await self.graph.aget_state(config={"configurable": {"thread_id": simulation_id}})
            
            # Extract results
            result = self._extract_simulation_result(simulation_id, final_state.values)
            
            # Update simulation with results
            simulation["result"] = result
            simulation["status"] = SimulationStatus.COMPLETED
            simulation["progress"] = 1.0
            simulation["updated_at"] = datetime.utcnow()
            
            logger.info(f"Simulation {simulation_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in simulation {simulation_id}: {str(e)}", exc_info=True)
            await self._update_status(
                simulation_id, 
                SimulationStatus.FAILED, 
                simulation["progress"],
                error=str(e)
            )

    async def _update_status(
        self, 
        simulation_id: str, 
        status: SimulationStatus, 
        progress: float,
        error: str | None = None
    ) -> None:
        """Update simulation status"""
        simulation = self.simulations[simulation_id]
        simulation["status"] = status
        simulation["progress"] = progress
        simulation["updated_at"] = datetime.utcnow()
        if error:
            simulation["error"] = error
        
        # Send WebSocket update if manager is available
        if self.manager:
            await self.manager.send_update(
                simulation_id,
                {
                    "type": "status_update",
                    "data": {
                        "status": status,
                        "progress": progress,
                        "error": error,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                }
            )

    async def _process_workflow_update(
        self, 
        simulation_id: str, 
        update: dict[str, Any]
    ) -> None:
        """Process updates from the workflow execution"""
        # Extract progress information from the update
        # LangGraph sends updates with node names as keys
        
        # Check for any node updates (not just orchestrator)
        state = None
        updated_node = None
        
        # Find which node was updated
        for node_name in ["orchestrator", "analyzer", "persona_generator", 
                          "persona_evaluator", "aggregator", "reporter"]:
            if node_name in update:
                state = update[node_name]
                updated_node = node_name
                break
        
        if state:
            # Get current phase from state or from orchestrator updates
            current_phase = state.get("current_phase")
            
            # If current phase not in this update, check if we can infer from node name
            if not current_phase and updated_node:
                node_to_phase = {
                    "analyzer": "analysis",
                    "persona_generator": "persona_generation",
                    "persona_evaluator": "evaluation",
                    "aggregator": "aggregation",
                    "reporter": "reporting",
                }
                current_phase = node_to_phase.get(updated_node)
            
            # Map phases to progress percentages
            phase_progress = {
                "initialization": 0.2,
                "analysis": 0.3,
                "persona_generation": 0.5,
                "evaluation": 0.7,
                "aggregation": 0.85,
                "reporting": 0.95,
                "completed": 1.0,
            }
            
            # Update progress if we have a valid phase
            if current_phase and current_phase in phase_progress:
                progress = phase_progress[current_phase]
                await self._update_status(simulation_id, SimulationStatus.RUNNING, progress)
            
            # Log phase transitions and send WebSocket updates
            if "messages" in state:
                for message in state["messages"]:
                    if isinstance(message, tuple) and len(message) > 1:
                        logger.info(f"Simulation {simulation_id} [{updated_node}]: {message[1]}")
                        # Send phase update via WebSocket
                        if self.manager:
                            await self.manager.send_update(
                                simulation_id,
                                {
                                    "type": "phase_update",
                                    "data": {
                                        "phase": current_phase or updated_node,
                                        "message": message[1],
                                        "node": updated_node,
                                        "timestamp": datetime.utcnow().isoformat(),
                                    }
                                }
                            )

    def _extract_simulation_result(
        self, 
        simulation_id: str, 
        final_state: ArticleReviewState
    ) -> SimulationResult:
        """Extract simulation result from final state"""
        from ..core.types import ArticleEvaluation, MarketSegment
        
        # Convert persona evaluations
        evaluations = []
        for eval_data in final_state.get("persona_evaluations", []):
            if isinstance(eval_data, dict) and "evaluation" in eval_data:
                eval_dict = eval_data["evaluation"]
                evaluations.append(ArticleEvaluation(**eval_dict))
        
        # Extract aggregation results
        agg_results = final_state.get("aggregation_results", {})
        
        # Convert market segments
        segments = []
        for segment_data in agg_results.get("market_segments", []):
            if isinstance(segment_data, dict):
                segments.append(MarketSegment(**segment_data))
        
        # Calculate processing time
        start_time = final_state.get("start_time", datetime.now())
        end_time = final_state.get("end_time") or datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return SimulationResult(
            simulation_id=simulation_id,
            total_personas=final_state.get("persona_count", 0),
            evaluations=evaluations,
            overall_relevance=agg_results.get("overall_relevance", 0.0),
            overall_quality=agg_results.get("overall_quality", 0.0),
            overall_engagement=agg_results.get("overall_engagement", 0.0),
            market_segments=segments,
            key_insights=agg_results.get("key_insights", []),
            recommendations=agg_results.get("recommendations", []),
            completed_at=end_time,
            processing_time_seconds=processing_time,
        )