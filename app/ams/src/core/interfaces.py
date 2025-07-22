"""
Core interfaces for the Article Market Simulator
"""

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from .types import (
    ActionResult,
    AgentID,
    PersonaAttributes,
    SimulationState,
)


@runtime_checkable
class IAgent(Protocol):
    """Interface for all agents in the simulation"""

    @property
    @abstractmethod
    def agent_id(self) -> AgentID:
        """Unique identifier for the agent"""
        ...

    @property
    @abstractmethod
    def attributes(self) -> PersonaAttributes:
        """Agent's persona attributes"""
        ...

    @abstractmethod
    async def perceive(self, environment: "IEnvironment") -> dict[str, Any]:
        """Perceive the current state of the environment"""
        ...

    @abstractmethod
    async def decide(self, perception: dict[str, Any]) -> "IAction":
        """Decide on an action based on perception"""
        ...

    @abstractmethod
    async def act(self, action: "IAction", environment: "IEnvironment") -> ActionResult:
        """Execute an action in the environment"""
        ...

    @abstractmethod
    async def update(self, result: ActionResult) -> None:
        """Update internal state based on action result"""
        ...


@runtime_checkable
class IEnvironment(Protocol):
    """Interface for the simulation environment"""

    @property
    @abstractmethod
    def state(self) -> SimulationState:
        """Current state of the environment"""
        ...

    @abstractmethod
    async def get_observable_state(self, agent_id: AgentID) -> dict[str, Any]:
        """Get the state observable by a specific agent"""
        ...

    @abstractmethod
    async def apply_action(self, agent_id: AgentID, action: "IAction") -> ActionResult:
        """Apply an agent's action to the environment"""
        ...

    @abstractmethod
    async def update_state(self) -> None:
        """Update the environment state"""
        ...

    @abstractmethod
    def add_agent(self, agent: IAgent) -> None:
        """Add an agent to the environment"""
        ...

    @abstractmethod
    def remove_agent(self, agent_id: AgentID) -> None:
        """Remove an agent from the environment"""
        ...

    @abstractmethod
    def get_agents(self) -> list[IAgent]:
        """Get all agents in the environment"""
        ...


@runtime_checkable
class IAction(Protocol):
    """Interface for agent actions"""

    @property
    @abstractmethod
    def action_type(self) -> str:
        """Type of action"""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """Action parameters"""
        ...

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the action is valid"""
        ...

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the action"""
        ...


@runtime_checkable
class IPlugin(Protocol):
    """Interface for simulation plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        ...

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the plugin with configuration"""
        ...

    @abstractmethod
    async def on_simulation_start(self, simulation: "ISimulation") -> None:
        """Called when simulation starts"""
        ...

    @abstractmethod
    async def on_timestep(self, simulation: "ISimulation", timestep: int) -> None:
        """Called on each simulation timestep"""
        ...

    @abstractmethod
    async def on_simulation_end(self, simulation: "ISimulation") -> None:
        """Called when simulation ends"""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        ...


@runtime_checkable
class ISimulation(Protocol):
    """Interface for the main simulation controller"""

    @property
    @abstractmethod
    def simulation_id(self) -> str:
        """Unique simulation identifier"""
        ...

    @property
    @abstractmethod
    def environment(self) -> IEnvironment:
        """The simulation environment"""
        ...

    @property
    @abstractmethod
    def current_timestep(self) -> int:
        """Current simulation timestep"""
        ...

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Whether the simulation is currently running"""
        ...

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the simulation"""
        ...

    @abstractmethod
    async def add_plugin(self, plugin: IPlugin) -> None:
        """Add a plugin to the simulation"""
        ...

    @abstractmethod
    async def run(self, max_timesteps: int) -> None:
        """Run the simulation for a specified number of timesteps"""
        ...

    @abstractmethod
    async def step(self) -> None:
        """Execute a single simulation timestep"""
        ...

    @abstractmethod
    async def pause(self) -> None:
        """Pause the simulation"""
        ...

    @abstractmethod
    async def resume(self) -> None:
        """Resume the simulation"""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the simulation"""
        ...

    @abstractmethod
    def get_results(self) -> dict[str, Any]:
        """Get simulation results"""
        ...


@runtime_checkable
class IVisualization(Protocol):
    """Interface for visualization components"""

    @abstractmethod
    async def connect(self, websocket) -> None:
        """Connect a websocket client"""
        ...

    @abstractmethod
    async def disconnect(self, websocket) -> None:
        """Disconnect a websocket client"""
        ...

    @abstractmethod
    async def send_update(self, data: dict[str, Any]) -> None:
        """Send update to all connected clients"""
        ...

    @abstractmethod
    async def send_differential_update(self, changes: dict[str, Any]) -> None:
        """Send only changes to connected clients"""
        ...

    @abstractmethod
    def prepare_visualization_data(self, simulation_state: SimulationState) -> dict[str, Any]:
        """Prepare data for visualization"""
        ...
