"""Base agent class for the AI Digital Assistant."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from google.adk.agents import Agent, LlmAgent, InvocationContext


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    instruction: str
    model: str = "gemini-2.5-flash"
    tools: List[Any] = Field(default_factory=list)
    sub_agents: List[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all custom agents."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self._agent: Optional[Agent] = None

    @property
    def agent(self) -> Agent:
        """Get or create the underlying ADK agent."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create the ADK agent instance."""
        pass

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given input."""
        pass


class LLMAgentWrapper(BaseAgent):
    """Wrapper for standard LLM-based agents."""

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.config.name,
            description=self.config.description,
            instruction=self.config.instruction,
            model=self.config.model,
            tools=self.config.tools,
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent."""
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService

        session_service = InMemorySessionService()
        runner = Runner(
            agent=self.agent,
            app_name="ai-assistant",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="ai-assistant",
            user_id=input_data.get("user_id", "default"),
        )

        result = await runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=input_data.get("message", ""),
        )

        return {"response": result, "session_id": session.id}
