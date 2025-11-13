import logging
import os
from typing import AsyncGenerator, Dict, Iterable

from agent_core.agent_registry import AgentRegistry
from agent_core.agent_tools import get_tool_specs

LOGGER = logging.getLogger(__name__)

MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1"

Agent = None
Runner = None
SQLiteSession = None
SDK_AVAILABLE = False

if not MOCK_MODE:
    try:  # pragma: no cover - guarded import
        from agents import Agent, Runner, SQLiteSession  # type: ignore

        SDK_AVAILABLE = True
    except Exception as exc:  # pragma: no cover - import guard
        LOGGER.warning("OpenAI Agents SDK unavailable, falling back to offline mode: %s", exc)
        SDK_AVAILABLE = False


class AgentRuntime:
    """Wrapper around OpenAI Agents SDK.  Manages sessions and runs agents."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.sessions = {}  # (agent_id, session_id) -> session

    def _get_session(self, agent_id: str, session_id: str):
        if not self._can_use_sdk():
            return None
        key = (agent_id, session_id)
        if key not in self.sessions:
            self.sessions[key] = SQLiteSession(f"{agent_id}:{session_id}")
        return self.sessions[key]

    def close_session(self, session_id: str):
        keys_to_delete = [k for k in self.sessions.keys() if k[1] == session_id]
        for k in keys_to_delete:
            del self.sessions[k]

    async def generate(
        self, agent_id: str, user_input: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        config = self.registry.get_agent(agent_id)

        if self._can_use_sdk():
            try:
                async for chunk in self._stream_from_sdk(config, user_input, session_id):
                    yield chunk
                return
            except Exception as exc:  # pragma: no cover - network/runtime failure
                LOGGER.warning("Falling back to offline response due to SDK error: %s", exc)

        for chunk in self._offline_response(config, user_input):
            yield chunk

    def _can_use_sdk(self) -> bool:
        return (not MOCK_MODE) and SDK_AVAILABLE and bool(os.getenv("OPENAI_API_KEY"))

    async def _stream_from_sdk(
        self, config: Dict[str, str], user_input: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        tools = get_tool_specs(config.get("tools", []))

        agent = Agent(
            name=config["name"],
            instructions=config["system_prompt"],
            model_config={"model": config.get("model", "gpt-4.1-mini")},
            tools=tools,
        )
        session = self._get_session(config["id"], session_id)
        result = Runner.run_sync(agent, user_input, session=session)
        yield str(result.final_output)

    def _offline_response(self, config: Dict[str, str], user_input: str) -> Iterable[str]:
        """Generate a friendly deterministic message when the SDK is unavailable."""

        system_hint = (config.get("system_prompt") or "You are a helpful assistant.").strip()
        first_sentence = system_hint.split(". ")[0].strip()
        intro = first_sentence if first_sentence else "I'm ready to help."
        response = (
            f"[{config.get('name', 'Agent')}] {intro} "
            f"Here is a short reply to '{user_input}': "
            f"{user_input[::-1]}"
        )
        for word in response.split(" "):
            yield word + " "
