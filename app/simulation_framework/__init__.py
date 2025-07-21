"""
Generalized Multi-Agent Simulation Framework

A flexible, extensible framework for building various types of market simulations
with real-time visualization capabilities.
"""

from .core import (
    # Base interfaces
    IAgent,
    IAction,
    IEnvironment,
    ISimulationPlugin,
    
    # Core classes
    SimulationEvent,
    SimulationState,
    EventBus,
    SimulationClock,
    StreamableState,
    SimulationDataStream,
    MetricsCollector
)

from .engine import (
    SimulationEngine,
    SimulationController
)

from .visualization import (
    VisualizationBridge,
    VisualizationServer,
    DataExporter
)

__version__ = "1.0.0"
__author__ = "Simulation Framework Team"

__all__ = [
    # Core interfaces
    "IAgent",
    "IAction", 
    "IEnvironment",
    "ISimulationPlugin",
    
    # Core classes
    "SimulationEvent",
    "SimulationState",
    "EventBus",
    "SimulationClock",
    "StreamableState",
    "SimulationDataStream",
    "MetricsCollector",
    
    # Engine
    "SimulationEngine",
    "SimulationController",
    
    # Visualization
    "VisualizationBridge",
    "VisualizationServer",
    "DataExporter"
]