import uuid
import json
import os
from typing import List, Dict, Any, Optional

class AgentRegistry:
    """
    File‑based registry storing agent configs as JSON files.
    """
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(self.base_path, exist_ok=True)

    def _agent_path(self, agent_id: str) -> str:
        return os.path.join(self.base_path, f"{agent_id}.json")

    def list_agents(self) -> List[Dict[str, Any]]:
        agents = []
        for fname in os.listdir(self.base_path):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self.base_path, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                agents.append(json.load(f))
        return agents

    def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = str(uuid.uuid4())
        config = {
            "id": agent_id,
            "name": config.get("name", f"Agent {agent_id[:8]}"),
            "model": config.get("model", "gpt-4.1-mini"),
            "system_prompt": config.get("system_prompt", "You are a helpful assistant."),
            "tools": config.get("tools", []),
        }
        with open(self._agent_path(agent_id), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return config

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        fpath = self._agent_path(agent_id)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Agent {agent_id} not found")
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing agent and return the updated record.

        This method works with dictionaries (the format returned by get_agent)
        instead of trying to access attributes on objects. Only provided fields
        are updated; missing fields are left as-is.
        """
        fpath = self._agent_path(agent_id)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Agent {agent_id} not found")

        with open(fpath, "r", encoding="utf-8") as f:
            agent = json.load(f)

        for key, value in updates.items():
            if value is not None:
                agent[key] = value

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(agent, f, indent=2)

        return agent

    def get_agent_tree(self, root_agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Return a minimal agent tree for the given root agent.

        The current implementation has no persisted hierarchy, but this method
        still returns a consistent dictionary shape and uses dictionary access
        to avoid AttributeError when called.
        """
        try:
            agent = self.get_agent(root_agent_id)
        except FileNotFoundError:
            return None

        return {
            "id": agent.get("id"),
            "name": agent.get("name"),
            "model": agent.get("model"),
            "children": [],  # Placeholder until hierarchy is implemented
        }

    def find_delegation_chain(self, task_type: str, root_agent_id: str) -> List[str]:
        """
        Return a delegation chain starting from the root agent.

        Uses dictionary keys instead of attribute access to avoid runtime errors.
        The simplified implementation returns the root agent id when present.
        """
        try:
            agent = self.get_agent(root_agent_id)
        except FileNotFoundError:
            return []

        return [agent.get("id")]