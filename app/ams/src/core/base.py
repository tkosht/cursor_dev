"""
Base implementations of core interfaces
"""

import logging
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Any

from .interfaces import IAction, IAgent, IEnvironment, IPlugin, ISimulation
from .types import (
    ActionResult,
    AgentID,
    PersonaAttributes,
    SimulationState,
)

logger = logging.getLogger(__name__)


class BaseAction(IAction):
    """Base implementation of IAction"""

    def __init__(self, action_type: str, parameters: dict[str, Any]):
        self._action_type = action_type
        self._parameters = parameters or {}

    @property
    def action_type(self) -> str:
        return self._action_type

    @property
    def parameters(self) -> dict[str, Any]:
        return self._parameters

    def validate(self) -> bool:
        """Basic validation - can be overridden by subclasses"""
        return bool(self._action_type)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(type={self._action_type}, params={self._parameters})"

    def __repr__(self) -> str:
        return self.__str__()


class BaseAgent(IAgent):
    """Base implementation of IAgent"""

    def __init__(
        self,
        agent_id: AgentID | None = None,
        attributes: PersonaAttributes | None = None,
    ):
        self._agent_id = agent_id or str(uuid.uuid4())
        self._attributes = attributes or PersonaAttributes()
        self._state: dict[str, Any] = {}
        self._action_history: list[ActionResult] = []

    @property
    def agent_id(self) -> AgentID:
        return self._agent_id

    @property
    def attributes(self) -> PersonaAttributes:
        return self._attributes

    async def perceive(self, environment: IEnvironment) -> dict[str, Any]:
        """Default perception - gets observable state from environment"""
        return await environment.get_observable_state(self._agent_id)

    @abstractmethod
    async def decide(self, perception: dict[str, Any]) -> IAction:
        """Must be implemented by subclasses"""
        pass

    async def act(
        self, action: IAction, environment: IEnvironment
    ) -> ActionResult:
        """Execute action in environment"""
        result = await environment.apply_action(self._agent_id, action)
        self._action_history.append(result)
        return result

    async def update(self, result: ActionResult) -> None:
        """Update internal state based on action result"""
        self._state["last_action_result"] = result
        logger.debug(
            f"Agent {self._agent_id} updated with result: {result.success}"
        )


class BaseEnvironment(IEnvironment):
    """Base implementation of IEnvironment"""

    def __init__(self):
        self._state = SimulationState()
        self._agents: dict[AgentID, IAgent] = {}
        self._action_queue: list[tuple[AgentID, IAction]] = []

    @property
    def state(self) -> SimulationState:
        return self._state

    async def get_observable_state(self, agent_id: AgentID) -> dict[str, Any]:
        """Get state observable by a specific agent"""
        # Default implementation - agents can see basic state info
        return {
            "timestep": self._state.timestep,
            "num_agents": len(self._agents),
            "article_metadata": self._state.article_metadata,
            "my_connections": self._state.agents.get(
                agent_id, PersonaAttributes()
            ).connections,
        }

    @abstractmethod
    async def apply_action(
        self, agent_id: AgentID, action: IAction
    ) -> ActionResult:
        """Must be implemented by subclasses"""
        pass

    async def update_state(self) -> None:
        """Update environment state"""
        self._state.timestep += 1
        # Process any queued actions
        while self._action_queue:
            agent_id, action = self._action_queue.pop(0)
            await self.apply_action(agent_id, action)

    def add_agent(self, agent: IAgent) -> None:
        """Add an agent to the environment"""
        self._agents[agent.agent_id] = agent
        self._state.agents[agent.agent_id] = agent.attributes
        logger.info(f"Added agent {agent.agent_id} to environment")

    def remove_agent(self, agent_id: AgentID) -> None:
        """Remove an agent from the environment"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            del self._state.agents[agent_id]
            logger.info(f"Removed agent {agent_id} from environment")

    def get_agents(self) -> list[IAgent]:
        """Get all agents in the environment"""
        return list(self._agents.values())


class BasePlugin(IPlugin):
    """Base implementation of IPlugin"""

    def __init__(
        self, name: str, version: str = "1.0.0", description: str = ""
    ):
        self._name = name
        self._version = version
        self._description = description
        self._config: dict[str, Any] = {}
        self._initialized = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def description(self) -> str:
        return self._description

    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the plugin"""
        self._config = config
        self._initialized = True
        logger.info(f"Initialized plugin {self._name} v{self._version}")

    async def on_simulation_start(self, simulation: ISimulation) -> None:
        """Called when simulation starts"""
        logger.debug(
            f"Plugin {self._name}: Simulation {simulation.simulation_id} started"
        )

    async def on_timestep(
        self, simulation: ISimulation, timestep: int
    ) -> None:
        """Called on each simulation timestep"""
        pass  # Default: do nothing

    async def on_simulation_end(self, simulation: ISimulation) -> None:
        """Called when simulation ends"""
        logger.debug(
            f"Plugin {self._name}: Simulation {simulation.simulation_id} ended"
        )

    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        self._initialized = False
        logger.info(f"Cleaned up plugin {self._name}")


class BaseSimulation(ISimulation):
    """Base implementation of ISimulation"""

    def __init__(self, environment: IEnvironment):
        self._simulation_id = str(uuid.uuid4())
        self._environment = environment
        self._current_timestep = 0
        self._is_running = False
        self._plugins: list[IPlugin] = []
        self._results: dict[str, Any] = {}
        self._start_time: datetime | None = None
        self._end_time: datetime | None = None

    @property
    def simulation_id(self) -> str:
        return self._simulation_id

    @property
    def environment(self) -> IEnvironment:
        return self._environment

    @property
    def current_timestep(self) -> int:
        return self._current_timestep

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the simulation"""
        logger.info(f"Initializing simulation {self._simulation_id}")
        # Initialize plugins
        for plugin in self._plugins:
            await plugin.initialize(
                config.get("plugins", {}).get(plugin.name, {})
            )

    async def add_plugin(self, plugin: IPlugin) -> None:
        """Add a plugin to the simulation"""
        self._plugins.append(plugin)
        logger.info(f"Added plugin {plugin.name} to simulation")

    async def run(self, max_timesteps: int) -> None:
        """Run the simulation"""
        logger.info(
            f"Starting simulation {self._simulation_id} for {max_timesteps} timesteps"
        )
        self._start_time = datetime.now()
        self._is_running = True

        # Notify plugins of start
        for plugin in self._plugins:
            await plugin.on_simulation_start(self)

        # Main simulation loop
        for _ in range(max_timesteps):
            if not self._is_running:
                break
            await self.step()

        # End simulation
        await self.stop()

    async def step(self) -> None:
        """Execute a single simulation timestep"""
        self._current_timestep += 1

        # Get all agents
        agents = self._environment.get_agents()

        # Agent perception-decision-action loop
        for agent in agents:
            # Perceive
            perception = await agent.perceive(self._environment)

            # Decide
            action = await agent.decide(perception)

            # Act
            result = await agent.act(action, self._environment)

            # Update agent state
            await agent.update(result)

        # Update environment
        await self._environment.update_state()

        # Notify plugins
        for plugin in self._plugins:
            await plugin.on_timestep(self, self._current_timestep)

        logger.debug(f"Completed timestep {self._current_timestep}")

    async def pause(self) -> None:
        """Pause the simulation"""
        self._is_running = False
        logger.info("Simulation paused")

    async def resume(self) -> None:
        """Resume the simulation"""
        self._is_running = True
        logger.info("Simulation resumed")

    async def stop(self) -> None:
        """Stop the simulation"""
        self._is_running = False
        self._end_time = datetime.now()

        # Notify plugins
        for plugin in self._plugins:
            await plugin.on_simulation_end(self)
            await plugin.cleanup()

        logger.info(f"Simulation {self._simulation_id} stopped")

    def get_results(self) -> dict[str, Any]:
        """Get simulation results"""
        return {
            "simulation_id": self._simulation_id,
            "total_timesteps": self._current_timestep,
            "start_time": (
                self._start_time.isoformat() if self._start_time else None
            ),
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration": (
                (self._end_time - self._start_time).total_seconds()
                if self._start_time and self._end_time
                else None
            ),
            "environment_state": self._environment.state.to_dict(),
            **self._results,
        }
