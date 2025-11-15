"""
Base module interface for Chimera agent modules
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..models.agent_state import AgentState


class BaseModule(ABC):
    """
    Base class for all agent modules.
    Each module represents a specific capability of the autonomous agent.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the module with configuration

        Args:
            config: Module-specific configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute the module's main functionality

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        pass

    def log(self, state: AgentState, message: str) -> None:
        """
        Add a log message to the agent state

        Args:
            state: Agent state
            message: Log message
        """
        state.add_log(f"[{self.name}] {message}")

    async def can_execute(self, state: AgentState) -> bool:
        """
        Check if this module can execute given the current state

        Args:
            state: Current agent state

        Returns:
            True if module can execute, False otherwise
        """
        return True

    def get_required_budget(self, state: AgentState) -> float:
        """
        Estimate the budget required for this module's execution

        Args:
            state: Current agent state

        Returns:
            Estimated cost in USD
        """
        return 0.0
