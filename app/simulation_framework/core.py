"""
Core components of the generalized multi-agent simulation framework.

This module provides the foundational abstractions and base implementations
for building various types of market simulations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque
import asyncio
import json
import itertools
import logging
from asyncio import Queue

logger = logging.getLogger(__name__)

T = TypeVar('T')

# ============================================================================
# Core Data Structures
# ============================================================================

@dataclass
class SimulationEvent:
    """Base event class for all simulation events"""
    timestamp: datetime
    source_id: str
    event_type: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'source_id': self.source_id,
            'event_type': self.event_type,
            'payload': self.payload,
            'metadata': self.metadata
        }


@dataclass 
class SimulationState:
    """Represents the current state of the simulation"""
    current_time: float
    total_agents: int
    active_agents: int
    total_events: int
    custom_state: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Abstract Interfaces
# ============================================================================

class IAgent(ABC):
    """Abstract base for all simulation agents"""
    
    def __init__(self, agent_id: str):
        self._agent_id = agent_id
        self._state: Dict[str, Any] = {}
        self._action_queue: List['IAction'] = []
    
    @property
    def agent_id(self) -> str:
        """Unique identifier for the agent"""
        return self._agent_id
    
    @abstractmethod
    async def perceive(self, environment: 'IEnvironment', events: List[SimulationEvent]) -> None:
        """Process incoming events and update internal state"""
        pass
    
    @abstractmethod
    async def decide(self) -> List['IAction']:
        """Make decisions based on current state"""
        pass
    
    @abstractmethod
    async def act(self, environment: 'IEnvironment') -> List[SimulationEvent]:
        """Execute actions and return resulting events"""
        pass
    
    def get_observable_state(self) -> Dict[str, Any]:
        """Return state visible to external observers"""
        return self._state.copy()


class IAction(ABC):
    """Abstract base for agent actions"""
    
    def __init__(self, action_type: str):
        self.action_type = action_type
        self.timestamp = datetime.now()
    
    @abstractmethod
    def validate(self, agent: IAgent, environment: 'IEnvironment') -> bool:
        """Check if action is valid in current context"""
        pass
    
    @abstractmethod
    async def execute(self, agent: IAgent, environment: 'IEnvironment') -> List[SimulationEvent]:
        """Execute the action and return events"""
        pass


class IEnvironment(ABC):
    """Abstract simulation environment"""
    
    def __init__(self):
        self._global_state: Dict[str, Any] = {}
        self._agent_states: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    async def update(self, timestep: float) -> List[SimulationEvent]:
        """Update environment state"""
        pass
    
    @abstractmethod
    def get_state(self, agent_id: str) -> Dict[str, Any]:
        """Get observable state for an agent"""
        pass
    
    @abstractmethod
    async def apply_action(self, action: IAction, agent: IAgent) -> List[SimulationEvent]:
        """Apply an agent action to the environment"""
        pass
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get complete environment snapshot"""
        return {
            'global_state': self._global_state.copy(),
            'agent_count': len(self._agent_states)
        }


class ISimulationPlugin(ABC):
    """Base interface for simulation type plugins"""
    
    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        """Factory method for creating domain-specific agents"""
        pass
    
    @abstractmethod
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        """Factory method for creating domain-specific environment"""
        pass
    
    @abstractmethod
    def get_metrics_definitions(self) -> Dict[str, Any]:
        """Define domain-specific metrics"""
        pass
    
    def get_visualization_config(self) -> Dict[str, Any]:
        """Return visualization configuration"""
        return {
            'default_charts': ['agent_count', 'event_rate'],
            'custom_visualizations': []
        }


# ============================================================================
# Event System
# ============================================================================

class EventBus:
    """Central event distribution system with async support"""
    
    def __init__(self, max_history: int = 10000):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: deque = deque(maxlen=max_history)
        self._stream_handlers: List[Callable] = []
        self._event_filters: List[Callable] = []
        self._metrics = {
            'total_events': 0,
            'events_by_type': {}
        }
    
    async def publish(self, event: SimulationEvent) -> None:
        """Publish event to all subscribers"""
        # Apply filters
        for filter_func in self._event_filters:
            if not filter_func(event):
                return
        
        # Store in history
        self._event_history.append(event)
        self._update_metrics(event)
        
        # Notify specific subscribers
        if event.event_type in self._subscribers:
            await asyncio.gather(*[
                handler(event) for handler in self._subscribers[event.event_type]
            ], return_exceptions=True)
        
        # Notify stream handlers for real-time visualization
        if self._stream_handlers:
            await asyncio.gather(*[
                handler(event) for handler in self._stream_handlers
            ], return_exceptions=True)
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to specific event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
    
    def add_stream_handler(self, handler: Callable) -> None:
        """Add handler for real-time event streaming"""
        self._stream_handlers.append(handler)
    
    def add_event_filter(self, filter_func: Callable) -> None:
        """Add event filter"""
        self._event_filters.append(filter_func)
    
    def get_event_history(self, event_type: Optional[str] = None, limit: Optional[int] = None) -> List[SimulationEvent]:
        """Get filtered event history"""
        events = list(self._event_history)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def _update_metrics(self, event: SimulationEvent) -> None:
        """Update internal metrics"""
        self._metrics['total_events'] += 1
        
        if event.event_type not in self._metrics['events_by_type']:
            self._metrics['events_by_type'][event.event_type] = 0
        self._metrics['events_by_type'][event.event_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return self._metrics.copy()


# ============================================================================
# Time Management
# ============================================================================

class SimulationClock:
    """Manages simulation time and scheduling"""
    
    def __init__(self, tick_rate: float = 0.1, time_scale: float = 1.0):
        self.current_time: float = 0.0
        self.tick_rate = tick_rate
        self.time_scale = time_scale  # Simulation time multiplier
        self.scheduled_events: List[Tuple[float, SimulationEvent]] = []
        self.tick_count: int = 0
    
    async def advance(self) -> List[SimulationEvent]:
        """Advance simulation time and return due events"""
        self.current_time += self.tick_rate * self.time_scale
        self.tick_count += 1
        
        due_events = []
        remaining_events = []
        
        for scheduled_time, event in self.scheduled_events:
            if scheduled_time <= self.current_time:
                # Update event timestamp
                event.timestamp = datetime.now()
                event.metadata['scheduled_time'] = scheduled_time
                event.metadata['execution_time'] = self.current_time
                due_events.append(event)
            else:
                remaining_events.append((scheduled_time, event))
        
        self.scheduled_events = remaining_events
        return due_events
    
    def schedule_event(self, event: SimulationEvent, delay: float) -> None:
        """Schedule future event"""
        scheduled_time = self.current_time + delay
        self.scheduled_events.append((scheduled_time, event))
        self.scheduled_events.sort(key=lambda x: x[0])
    
    def get_info(self) -> Dict[str, Any]:
        """Get clock information"""
        return {
            'current_time': self.current_time,
            'tick_rate': self.tick_rate,
            'time_scale': self.time_scale,
            'tick_count': self.tick_count,
            'scheduled_events': len(self.scheduled_events)
        }


# ============================================================================
# Data Streaming
# ============================================================================

@dataclass
class StreamableState:
    """Optimized state representation for streaming"""
    timestamp: float
    tick: int
    agent_states: Dict[str, Dict[str, Any]]
    environment_snapshot: Dict[str, Any]
    metrics: Dict[str, float]
    events_summary: Dict[str, int]
    
    def to_json(self) -> str:
        """Fast JSON serialization"""
        return json.dumps({
            'timestamp': self.timestamp,
            'tick': self.tick,
            'agents': self.agent_states,
            'environment': self.environment_snapshot,
            'metrics': self.metrics,
            'events': self.events_summary
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StreamableState':
        """Deserialize from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class SimulationDataStream:
    """Manages data streaming for visualization with backpressure handling"""
    
    def __init__(self, buffer_size: int = 1000, batch_size: int = 10):
        self.buffer = deque(maxlen=buffer_size)
        self.subscribers: List[Callable] = []
        self.batch_size = batch_size
        self._pending_batch: List[StreamableState] = []
        self._lock = asyncio.Lock()
    
    async def push(self, state: StreamableState) -> None:
        """Add state to stream with batching"""
        async with self._lock:
            self._pending_batch.append(state)
            self.buffer.append(state)
            
            if len(self._pending_batch) >= self.batch_size:
                await self._flush_batch()
    
    async def _flush_batch(self) -> None:
        """Flush pending batch to subscribers"""
        if not self._pending_batch:
            return
        
        batch = self._pending_batch.copy()
        self._pending_batch.clear()
        
        # Notify subscribers with batch
        await asyncio.gather(*[
            subscriber(batch) for subscriber in self.subscribers
        ], return_exceptions=True)
    
    def subscribe(self, handler: Callable) -> None:
        """Subscribe to data stream"""
        self.subscribers.append(handler)
    
    def unsubscribe(self, handler: Callable) -> None:
        """Unsubscribe from data stream"""
        if handler in self.subscribers:
            self.subscribers.remove(handler)
    
    def get_buffer(self, n: Optional[int] = None) -> List[StreamableState]:
        """Get last n states from buffer"""
        if n is None:
            return list(self.buffer)
        return list(itertools.islice(self.buffer, max(0, len(self.buffer) - n), len(self.buffer)))
    
    async def close(self) -> None:
        """Flush remaining data and close stream"""
        async with self._lock:
            if self._pending_batch:
                await self._flush_batch()


# ============================================================================
# Metrics System
# ============================================================================

class MetricsCollector:
    """Collects and aggregates simulation metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, List[Tuple[float, float]]] = {}
        self._aggregators: Dict[str, Callable] = {}
        self._windows: Dict[str, int] = {}  # Rolling window sizes
    
    def register_metric(self, name: str, aggregator: Callable = None, window_size: int = 100):
        """Register a new metric"""
        self._metrics[name] = []
        self._aggregators[name] = aggregator or (lambda x: sum(x) / len(x) if x else 0)
        self._windows[name] = window_size
    
    def record(self, name: str, value: float, timestamp: float):
        """Record a metric value"""
        if name not in self._metrics:
            self.register_metric(name)
        
        self._metrics[name].append((timestamp, value))
        
        # Maintain window size
        if len(self._metrics[name]) > self._windows[name]:
            self._metrics[name] = self._metrics[name][-self._windows[name]:]
    
    def get_current_value(self, name: str) -> Optional[float]:
        """Get most recent value for metric"""
        if name in self._metrics and self._metrics[name]:
            return self._metrics[name][-1][1]
        return None
    
    def get_aggregated_value(self, name: str) -> Optional[float]:
        """Get aggregated value for metric"""
        if name not in self._metrics:
            return None
        
        values = [v for _, v in self._metrics[name]]
        if not values:
            return None
        
        return self._aggregators[name](values)
    
    def get_time_series(self, name: str, limit: Optional[int] = None) -> List[Tuple[float, float]]:
        """Get time series data for metric"""
        if name not in self._metrics:
            return []
        
        data = self._metrics[name]
        if limit:
            data = data[-limit:]
        
        return data
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metric values"""
        return {
            name: {
                'current': self.get_current_value(name),
                'aggregated': self.get_aggregated_value(name),
                'count': len(self._metrics.get(name, []))
            }
            for name in self._metrics
        }