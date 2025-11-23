import os
from typing import AsyncGenerator

from agent_core.agent_registry import AgentRegistry
from agent_core.agent_tools import get_tool_specs

MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1"

if not MOCK_MODE:
    from agents import Agent, Runner, SQLiteSession
else:
    Agent = None
    Runner = None
    SQLiteSession = None

class AgentRuntime:
    """
    Wrapper around OpenAI Agents SDK.  Manages sessions and runs agents.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.sessions = {}  # (agent_id, session_id) -> session

    def _get_session(self, agent_id: str, session_id: str):
        if MOCK_MODE:
            return None
        key = (agent_id, session_id)
        if key not in self.sessions:
            self.sessions[key] = SQLiteSession(f"{agent_id}:{session_id}")
        return self.sessions[key]

    def close_session(self, session_id: str):
        keys_to_delete = [k for k in self.sessions.keys() if k[1] == session_id]
        for k in keys_to_delete:
            del self.sessions[k]

    async def generate(self, agent_id: str, user_input: str, session_id: str) -> AsyncGenerator[str, None]:
        config = self.registry.get_agent(agent_id)

        if MOCK_MODE:
            yield f"[MOCK_RESPONSE from {config['name']}] You said: {user_input}"
            return

        tools = get_tool_specs(config.get("tools", []))

        agent = Agent(
            name=config["name"],
            instructions=config["system_prompt"],
            model_config={"model": config.get("model", "gpt-4.1-mini")},
            tools=tools,
        )
        session = self._get_session(agent_id, session_id)
        result = Runner.run_sync(agent, user_input, session=session)
        text = str(result.final_output)
        yield text