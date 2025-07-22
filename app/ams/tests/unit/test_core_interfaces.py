"""
Unit tests for core interfaces
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from core.interfaces import IAgent, IEnvironment, IAction, IPlugin, ISimulation
from core.base import BaseAction, BaseAgent, BaseEnvironment, BasePlugin, BaseSimulation
from core.types import AgentID, PersonaAttributes, ActionResult, SimulationState


class TestBaseAction:
    """Test BaseAction implementation"""
    
    def test_action_creation(self):
        """Test creating a basic action"""
        action = BaseAction("test_action", {"param1": "value1"})
        
        assert action.action_type == "test_action"
        assert action.parameters == {"param1": "value1"}
        assert action.validate() is True
    
    def test_action_string_representation(self):
        """Test action string representation"""
        action = BaseAction("move", {"direction": "north"})
        
        assert "move" in str(action)
        assert "north" in str(action)
    
    def test_action_validation(self):
        """Test action validation"""
        # Valid action
        action1 = BaseAction("valid_action", {})
        assert action1.validate() is True
        
        # Invalid action (empty type)
        action2 = BaseAction("", {})
        assert action2.validate() is False


class TestBaseAgent:
    """Test BaseAgent implementation"""
    
    def test_agent_creation(self):
        """Test creating a basic agent"""
        agent = BaseAgent()
        
        assert isinstance(agent.agent_id, str)
        assert isinstance(agent.attributes, PersonaAttributes)
    
    def test_agent_with_custom_attributes(self):
        """Test agent with custom attributes"""
        attrs = PersonaAttributes(
            age=30,
            occupation="Engineer",
            values=["innovation", "quality"]
        )
        agent = BaseAgent(agent_id="test-123", attributes=attrs)
        
        assert agent.agent_id == "test-123"
        assert agent.attributes.age == 30
        assert agent.attributes.occupation == "Engineer"
    
    @pytest.mark.asyncio
    async def test_agent_perceive(self):
        """Test agent perception"""
        agent = BaseAgent()
        mock_env = MagicMock(spec=IEnvironment)
        mock_env.get_observable_state = AsyncMock(return_value={"test": "data"})
        
        perception = await agent.perceive(mock_env)
        
        assert perception == {"test": "data"}
        mock_env.get_observable_state.assert_called_once_with(agent.agent_id)
    
    @pytest.mark.asyncio
    async def test_agent_act(self):
        """Test agent action execution"""
        agent = BaseAgent()
        action = BaseAction("test_action", {})
        
        mock_env = MagicMock(spec=IEnvironment)
        expected_result = ActionResult(
            success=True,
            action_type="test_action",
            agent_id=agent.agent_id
        )
        mock_env.apply_action = AsyncMock(return_value=expected_result)
        
        result = await agent.act(action, mock_env)
        
        assert result.success is True
        assert result.action_type == "test_action"
        mock_env.apply_action.assert_called_once_with(agent.agent_id, action)
    
    @pytest.mark.asyncio
    async def test_agent_update(self):
        """Test agent state update"""
        agent = BaseAgent()
        result = ActionResult(
            success=True,
            action_type="test_action",
            agent_id=agent.agent_id,
            effects={"health": -10}
        )
        
        await agent.update(result)
        
        assert agent._state["last_action_result"] == result
        assert len(agent._action_history) == 0  # Not added in update, only in act


class TestBaseEnvironment:
    """Test BaseEnvironment implementation"""
    
    def test_environment_creation(self):
        """Test creating a basic environment"""
        env = BaseEnvironment()
        
        assert isinstance(env.state, SimulationState)
        assert env.state.timestep == 0
        assert len(env.get_agents()) == 0
    
    def test_add_remove_agents(self):
        """Test adding and removing agents"""
        env = BaseEnvironment()
        agent1 = BaseAgent(agent_id="agent-1")
        agent2 = BaseAgent(agent_id="agent-2")
        
        # Add agents
        env.add_agent(agent1)
        env.add_agent(agent2)
        
        assert len(env.get_agents()) == 2
        assert agent1 in env.get_agents()
        assert agent2 in env.get_agents()
        
        # Remove agent
        env.remove_agent("agent-1")
        
        assert len(env.get_agents()) == 1
        assert agent1 not in env.get_agents()
        assert agent2 in env.get_agents()
    
    @pytest.mark.asyncio
    async def test_get_observable_state(self):
        """Test getting observable state for agent"""
        env = BaseEnvironment()
        agent = BaseAgent(agent_id="test-agent")
        env.add_agent(agent)
        
        env.state.article_metadata = {"title": "Test Article"}
        
        observable = await env.get_observable_state("test-agent")
        
        assert observable["timestep"] == 0
        assert observable["num_agents"] == 1
        assert observable["article_metadata"]["title"] == "Test Article"
    
    @pytest.mark.asyncio
    async def test_update_state(self):
        """Test environment state update"""
        env = BaseEnvironment()
        initial_timestep = env.state.timestep
        
        await env.update_state()
        
        assert env.state.timestep == initial_timestep + 1


class TestBasePlugin:
    """Test BasePlugin implementation"""
    
    def test_plugin_creation(self):
        """Test creating a basic plugin"""
        plugin = BasePlugin(
            name="TestPlugin",
            version="1.0.0",
            description="A test plugin"
        )
        
        assert plugin.name == "TestPlugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "A test plugin"
        assert plugin._initialized is False
    
    @pytest.mark.asyncio
    async def test_plugin_initialization(self):
        """Test plugin initialization"""
        plugin = BasePlugin("TestPlugin")
        config = {"setting1": "value1"}
        
        await plugin.initialize(config)
        
        assert plugin._initialized is True
        assert plugin._config == config
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self):
        """Test plugin lifecycle methods"""
        plugin = BasePlugin("TestPlugin")
        mock_sim = MagicMock(spec=ISimulation)
        mock_sim.simulation_id = "test-sim"
        
        # These should not raise errors
        await plugin.on_simulation_start(mock_sim)
        await plugin.on_timestep(mock_sim, 1)
        await plugin.on_simulation_end(mock_sim)
        await plugin.cleanup()
        
        assert plugin._initialized is False  # After cleanup


class TestBaseSimulation:
    """Test BaseSimulation implementation"""
    
    def test_simulation_creation(self):
        """Test creating a basic simulation"""
        env = BaseEnvironment()
        sim = BaseSimulation(env)
        
        assert isinstance(sim.simulation_id, str)
        assert sim.environment == env
        assert sim.current_timestep == 0
        assert sim.is_running is False
    
    @pytest.mark.asyncio
    async def test_add_plugin(self):
        """Test adding plugins to simulation"""
        env = BaseEnvironment()
        sim = BaseSimulation(env)
        plugin = BasePlugin("TestPlugin")
        
        await sim.add_plugin(plugin)
        
        assert plugin in sim._plugins
    
    @pytest.mark.asyncio 
    async def test_simulation_step(self):
        """Test single simulation step"""
        env = BaseEnvironment()
        sim = BaseSimulation(env)
        
        # Add a mock agent
        agent = MagicMock(spec=IAgent)
        agent.perceive = AsyncMock(return_value={"test": "perception"})
        agent.decide = AsyncMock(return_value=BaseAction("test", {}))
        agent.act = AsyncMock(return_value=ActionResult(True, "test", "agent-1"))
        agent.update = AsyncMock()
        
        env.add_agent(agent)
        
        initial_timestep = sim.current_timestep
        
        await sim.step()
        
        assert sim.current_timestep == initial_timestep + 1
        agent.perceive.assert_called_once()
        agent.decide.assert_called_once()
        agent.act.assert_called_once()
        agent.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_simulation_run(self):
        """Test running simulation for multiple steps"""
        env = BaseEnvironment()
        sim = BaseSimulation(env)
        
        # Add plugin to track steps
        plugin = MagicMock(spec=IPlugin)
        plugin.initialize = AsyncMock()
        plugin.on_simulation_start = AsyncMock()
        plugin.on_timestep = AsyncMock()
        plugin.on_simulation_end = AsyncMock()
        plugin.cleanup = AsyncMock()
        
        await sim.add_plugin(plugin)
        
        # Run for 3 steps
        await sim.run(3)
        
        assert sim.current_timestep == 3
        assert sim.is_running is False
        plugin.on_simulation_start.assert_called_once()
        assert plugin.on_timestep.call_count == 3
        plugin.on_simulation_end.assert_called_once()
    
    def test_get_results(self):
        """Test getting simulation results"""
        env = BaseEnvironment()
        sim = BaseSimulation(env)
        sim._start_time = datetime.now()
        sim._current_timestep = 5
        
        results = sim.get_results()
        
        assert results["simulation_id"] == sim.simulation_id
        assert results["total_timesteps"] == 5
        assert "environment_state" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])