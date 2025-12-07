"""Agent orchestration engine for managing multi-agent systems."""
import asyncio
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .base import BaseAgent, AgentConfig


class OrchestratorConfig(BaseModel):
    """Configuration for the orchestrator."""
    name: str = "master_orchestrator"
    model: str = "gemini-3.0-pro"
    max_parallel_agents: int = 5
    timeout_seconds: int = 300


class AgentOrchestrator:
    """
    Central orchestration engine for managing multiple AI agents.

    Supports:
    - Sequential agent pipelines
    - Parallel agent execution
    - Dynamic agent routing
    - Agent handoffs
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self._agents: Dict[str, Agent] = {}
        self._session_service = InMemorySessionService()
        self._runners: Dict[str, Runner] = {}

    def register_agent(self, name: str, agent: Agent) -> None:
        """Register an agent with the orchestrator."""
        self._agents[name] = agent
        self._runners[name] = Runner(
            agent=agent,
            app_name="ai-assistant",
            session_service=self._session_service,
        )

    def create_agent(
        self,
        name: str,
        description: str,
        instruction: str,
        tools: List[Any] = None,
        model: str = None,
    ) -> Agent:
        """Create and register a new agent."""
        agent = Agent(
            name=name,
            description=description,
            instruction=instruction,
            model=model or self.config.model,
            tools=tools or [],
        )
        self.register_agent(name, agent)
        return agent

    def create_sequential_pipeline(
        self,
        name: str,
        agent_names: List[str],
        description: str = "",
    ) -> SequentialAgent:
        """Create a sequential pipeline of agents."""
        sub_agents = [self._agents[n] for n in agent_names if n in self._agents]
        pipeline = SequentialAgent(
            name=name,
            description=description or f"Sequential pipeline: {' -> '.join(agent_names)}",
            sub_agents=sub_agents,
        )
        self.register_agent(name, pipeline)
        return pipeline

    def create_parallel_group(
        self,
        name: str,
        agent_names: List[str],
        description: str = "",
    ) -> ParallelAgent:
        """Create a parallel execution group of agents."""
        sub_agents = [self._agents[n] for n in agent_names if n in self._agents]
        group = ParallelAgent(
            name=name,
            description=description or f"Parallel group: {', '.join(agent_names)}",
            sub_agents=sub_agents,
        )
        self.register_agent(name, group)
        return group

    async def run_agent(
        self,
        agent_name: str,
        message: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run a specific agent with a message."""
        if agent_name not in self._runners:
            raise ValueError(f"Agent '{agent_name}' not found")

        runner = self._runners[agent_name]

        if session_id is None:
            session = await self._session_service.create_session(
                app_name="ai-assistant",
                user_id=user_id,
            )
            session_id = session.id

        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            events.append(event)

        return {
            "agent": agent_name,
            "session_id": session_id,
            "events": events,
            "response": self._extract_response(events),
        }

    async def run_parallel(
        self,
        agent_messages: Dict[str, str],
        user_id: str = "default",
    ) -> Dict[str, Any]:
        """Run multiple agents in parallel."""
        tasks = [
            self.run_agent(name, msg, user_id)
            for name, msg in agent_messages.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(agent_messages.keys(), results))

    def _extract_response(self, events: List[Any]) -> str:
        """Extract the final response from events."""
        for event in reversed(events):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    return ''.join(
                        p.text for p in event.content.parts
                        if hasattr(p, 'text')
                    )
        return ""

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get a registered agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())

    def list_agent_details(self) -> List[Dict[str, Any]]:
        """List registered agents with descriptions and models."""
        details = []
        for name, agent in self._agents.items():
            details.append({
                "name": name,
                "description": getattr(agent, "description", ""),
                "model": getattr(agent, "model", self.config.model),
            })
        return details
