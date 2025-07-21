"""
Visualization and data streaming components for real-time simulation monitoring.

This module provides the infrastructure for streaming simulation data to
visualization clients via WebSocket and other protocols.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from collections import defaultdict
import numpy as np

from .core import (
    SimulationEvent, StreamableState, SimulationDataStream,
    IAgent, IEnvironment
)
from .engine import SimulationEngine

logger = logging.getLogger(__name__)


class VisualizationBridge:
    """Bridge between simulation engine and visualization layer"""
    
    def __init__(self, engine: SimulationEngine, config: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.config = config or {}
        self.data_stream = SimulationDataStream(
            buffer_size=config.get('buffer_size', 1000),
            batch_size=config.get('batch_size', 10)
        )
        
        # Sampling configuration
        self.sample_rate = config.get('sample_rate', 1)  # Sample every N ticks
        self.tick_counter = 0
        
        # Data aggregation
        self.aggregators: Dict[str, Callable] = {}
        self._setup_default_aggregators()
        
        # Register as event handler
        engine.event_bus.add_stream_handler(self._handle_event)
        
        # Visualization metadata
        self.viz_config = self._create_viz_config()
    
    def _setup_default_aggregators(self) -> None:
        """Setup default data aggregators"""
        self.aggregators['agent_count'] = lambda agents: len(agents)
        self.aggregators['active_agents'] = lambda agents: len([
            a for a in agents if not hasattr(a, 'is_active') or a.is_active
        ])
        self.aggregators['event_rate'] = self._calculate_event_rate
    
    def _create_viz_config(self) -> Dict[str, Any]:
        """Create visualization configuration"""
        plugin_viz_config = self.engine.plugin.get_visualization_config()
        
        return {
            'simulation_info': {
                'plugin_name': self.engine.plugin.get_plugin_info().get('name', 'Unknown'),
                'tick_rate': self.engine.clock.tick_rate,
                'time_scale': self.engine.clock.time_scale
            },
            'default_charts': plugin_viz_config.get('default_charts', []),
            'custom_visualizations': plugin_viz_config.get('custom_visualizations', []),
            'metrics': list(self.engine.plugin.get_metrics_definitions().keys()),
            'update_rate': self.sample_rate
        }
    
    async def _handle_event(self, event: SimulationEvent) -> None:
        """Handle simulation events and convert to streamable format"""
        # Sample based on rate
        if event.event_type != 'metrics_update':
            return
        
        self.tick_counter += 1
        if self.tick_counter % self.sample_rate != 0:
            return
        
        # Create streamable state
        state = await self._create_streamable_state(event)
        
        # Push to stream
        await self.data_stream.push(state)
    
    async def _create_streamable_state(self, event: SimulationEvent) -> StreamableState:
        """Create streamable state from current simulation state"""
        # Collect agent states efficiently
        agent_states = self._collect_agent_states()
        
        # Get environment snapshot
        env_snapshot = self._get_environment_snapshot()
        
        # Get metrics from event
        metrics = event.payload if event.event_type == 'metrics_update' else {}
        
        # Create events summary
        events_summary = self._create_events_summary()
        
        return StreamableState(
            timestamp=self.engine.clock.current_time,
            tick=self.engine.clock.tick_count,
            agent_states=agent_states,
            environment_snapshot=env_snapshot,
            metrics=metrics,
            events_summary=events_summary
        )
    
    def _collect_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Efficiently collect agent states for visualization"""
        states = {}
        
        for agent in self.engine.agents:
            # Get observable state
            agent_state = agent.get_observable_state()
            
            # Apply any visualization-specific transformations
            if hasattr(agent, 'get_viz_state'):
                agent_state = agent.get_viz_state()
            
            # Flatten complex structures for efficiency
            states[agent.agent_id] = self._flatten_state(agent_state)
        
        return states
    
    def _flatten_state(self, state: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dictionaries for efficient transmission"""
        flattened = {}
        
        for key, value in state.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict) and len(value) < 10:  # Don't flatten large dicts
                flattened.update(self._flatten_state(value, full_key))
            elif isinstance(value, (list, tuple)) and len(value) < 10:
                flattened[full_key] = value
            else:
                flattened[full_key] = value
        
        return flattened
    
    def _get_environment_snapshot(self) -> Dict[str, Any]:
        """Get environment snapshot for visualization"""
        snapshot = self.engine.environment.get_snapshot()
        
        # Add visualization-specific data if available
        if hasattr(self.engine.environment, 'get_viz_data'):
            snapshot['viz_data'] = self.engine.environment.get_viz_data()
        
        return snapshot
    
    def _create_events_summary(self) -> Dict[str, int]:
        """Create summary of recent events"""
        event_counts = defaultdict(int)
        
        # Count events in recent history
        recent_events = self.engine.event_bus.get_event_history(limit=100)
        for event in recent_events:
            event_counts[event.event_type] += 1
        
        return dict(event_counts)
    
    def _calculate_event_rate(self, agents: List[IAgent]) -> float:
        """Calculate event rate"""
        total_events = self.engine.event_bus.get_metrics()['total_events']
        time_elapsed = max(1, self.engine.clock.current_time)
        return total_events / time_elapsed
    
    def get_visualization_config(self) -> Dict[str, Any]:
        """Get visualization configuration"""
        return self.viz_config
    
    def get_current_state(self) -> Optional[StreamableState]:
        """Get current state for initial client connection"""
        buffer = self.data_stream.get_buffer(1)
        return buffer[0] if buffer else None


class VisualizationServer:
    """WebSocket server for real-time visualization"""
    
    def __init__(self, bridge: VisualizationBridge, host: str = 'localhost', port: int = 8765):
        self.bridge = bridge
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.client_configs: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        
        # Subscribe to data stream
        bridge.data_stream.subscribe(self._handle_stream_batch)
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'messages_sent': 0,
            'bytes_sent': 0
        }
    
    async def _handle_stream_batch(self, batch: List[StreamableState]) -> None:
        """Handle batch of states from data stream"""
        if not self.clients:
            return
        
        # Process batch based on client preferences
        for state in batch:
            await self._broadcast_state(state)
    
    async def _broadcast_state(self, state: StreamableState) -> None:
        """Broadcast state to all connected clients"""
        if not self.clients:
            return
        
        # Prepare message
        message = self._prepare_message(state)
        message_str = json.dumps(message)
        
        # Send to all clients
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                # Check client filters
                if self._should_send_to_client(client, state):
                    await client.send(message_str)
                    self.stats['messages_sent'] += 1
                    self.stats['bytes_sent'] += len(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.remove(client)
            if client in self.client_configs:
                del self.client_configs[client]
    
    def _prepare_message(self, state: StreamableState) -> Dict[str, Any]:
        """Prepare message for transmission"""
        return {
            'type': 'state_update',
            'timestamp': state.timestamp,
            'tick': state.tick,
            'data': {
                'agents': state.agent_states,
                'environment': state.environment_snapshot,
                'metrics': state.metrics,
                'events': state.events_summary
            }
        }
    
    def _should_send_to_client(self, client: WebSocketServerProtocol, state: StreamableState) -> bool:
        """Check if state should be sent to specific client"""
        config = self.client_configs.get(client, {})
        
        # Apply any client-specific filters
        if 'metric_filter' in config:
            # Only send if specific metrics are present
            required_metrics = config['metric_filter']
            if not all(m in state.metrics for m in required_metrics):
                return False
        
        if 'agent_filter' in config:
            # Only send if specific agents are present
            required_agents = config['agent_filter']
            if not any(a in state.agent_states for a in required_agents):
                return False
        
        return True
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        self.clients.add(websocket)
        self.stats['total_connections'] += 1
        client_id = id(websocket)
        
        logger.info(f"New visualization client connected: {client_id}")
        
        try:
            # Send initial configuration
            await self._send_initial_data(websocket)
            
            # Handle client messages
            async for message in websocket:
                await self._handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.clients.remove(websocket)
            if websocket in self.client_configs:
                del self.client_configs[websocket]
    
    async def _send_initial_data(self, websocket: WebSocketServerProtocol) -> None:
        """Send initial data to newly connected client"""
        # Send visualization configuration
        config_message = {
            'type': 'config',
            'data': self.bridge.get_visualization_config()
        }
        await websocket.send(json.dumps(config_message))
        
        # Send current state
        current_state = self.bridge.get_current_state()
        if current_state:
            await websocket.send(current_state.to_json())
        
        # Send historical data
        buffer = self.bridge.data_stream.get_buffer(100)
        if buffer:
            history_message = {
                'type': 'history',
                'data': [self._prepare_message(state) for state in buffer]
            }
            await websocket.send(json.dumps(history_message))
    
    async def _handle_client_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Handle message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'config':
                # Update client configuration
                self.client_configs[websocket] = data.get('config', {})
                
            elif message_type == 'control':
                # Handle simulation control commands
                await self._handle_control_message(data.get('command'), data.get('params', {}))
                
            elif message_type == 'query':
                # Handle data queries
                response = await self._handle_query(data.get('query'), data.get('params', {}))
                await websocket.send(json.dumps({
                    'type': 'query_response',
                    'id': data.get('id'),
                    'data': response
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def _handle_control_message(self, command: str, params: Dict[str, Any]) -> None:
        """Handle simulation control commands from client"""
        if command == 'pause':
            self.bridge.engine.pause()
        elif command == 'resume':
            self.bridge.engine.resume()
        elif command == 'stop':
            self.bridge.engine.stop()
        elif command == 'schedule_event':
            event = SimulationEvent(**params['event'])
            delay = params.get('delay', 0)
            self.bridge.engine.schedule_event(event, delay)
    
    async def _handle_query(self, query_type: str, params: Dict[str, Any]) -> Any:
        """Handle data queries from client"""
        if query_type == 'metrics_history':
            metric_name = params.get('metric')
            limit = params.get('limit', 100)
            return self.bridge.engine.metrics_collector.get_time_series(metric_name, limit)
        
        elif query_type == 'agent_details':
            agent_id = params.get('agent_id')
            for agent in self.bridge.engine.agents:
                if agent.agent_id == agent_id:
                    return agent.get_observable_state()
            return None
        
        elif query_type == 'event_history':
            event_type = params.get('event_type')
            limit = params.get('limit', 100)
            events = self.bridge.engine.event_bus.get_event_history(event_type, limit)
            return [e.to_dict() for e in events]
        
        return None
    
    async def start(self):
        """Start WebSocket server"""
        logger.info(f"Starting visualization server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            **self.stats,
            'active_connections': len(self.clients)
        }


class DataExporter:
    """Export simulation data for analysis"""
    
    def __init__(self, bridge: VisualizationBridge):
        self.bridge = bridge
        self.export_buffer: List[StreamableState] = []
        
        # Subscribe to data stream
        bridge.data_stream.subscribe(self._buffer_data)
    
    async def _buffer_data(self, batch: List[StreamableState]) -> None:
        """Buffer data for export"""
        self.export_buffer.extend(batch)
    
    def export_to_json(self, filepath: str, clear_buffer: bool = True) -> None:
        """Export buffered data to JSON file"""
        data = {
            'simulation_info': self.bridge.get_visualization_config()['simulation_info'],
            'states': [state.to_json() for state in self.export_buffer]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        if clear_buffer:
            self.export_buffer.clear()
    
    def export_metrics_to_csv(self, filepath: str) -> None:
        """Export metrics time series to CSV"""
        import csv
        
        metrics = self.bridge.engine.plugin.get_metrics_definitions().keys()
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = ['timestamp', 'tick'] + list(metrics)
            writer.writerow(header)
            
            # Data rows
            for state in self.export_buffer:
                row = [state.timestamp, state.tick]
                for metric in metrics:
                    row.append(state.metrics.get(metric, ''))
                writer.writerow(row)