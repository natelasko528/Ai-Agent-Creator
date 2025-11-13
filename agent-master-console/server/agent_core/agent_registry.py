import uuid
import json
import os
from typing import List, Dict, Any

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