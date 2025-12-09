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
        Update an agent configuration on disk and return the updated record.
        """
        agent = self.get_agent(agent_id)
        agent.update(updates)
        with open(self._agent_path(agent_id), "w", encoding="utf-8") as f:
            json.dump(agent, f, indent=2)
        return agent

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent configuration file. Returns True if removed.
        """
        fpath = self._agent_path(agent_id)
        if not os.path.exists(fpath):
            return False
        os.remove(fpath)
        return True

    def get_agent_tree(self, root_agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Build a simple parent/child tree using dictionary access.
        Agents may optionally define `parent_agent_id`; children are
        derived by scanning all agents on disk.
        """
        try:
            root_agent = self.get_agent(root_agent_id)
        except FileNotFoundError:
            return None

        def build(node: Dict[str, Any]) -> Dict[str, Any]:
            children = [
                a
                for a in self.list_agents()
                if a.get("parent_agent_id") == node.get("id")
            ]
            return {
                "id": node.get("id"),
                "name": node.get("name"),
                "model": node.get("model"),
                "agent_type": node.get("agent_type", "general"),
                "status": node.get("status", "active"),
                "children": [build(child) for child in children],
            }

        return build(root_agent)

    def find_delegation_chain(self, task_type: str, root_agent_id: str) -> List[str]:
        """
        Find a delegation chain based on an agent's capabilities.
        Returns a list of agent IDs from root to the agent that can
        handle the requested task_type. Uses dictionary access to
        avoid AttributeError when the registry returns dicts.
        """
        agents = {agent["id"]: agent for agent in self.list_agents()}

        def dfs(agent_id: str) -> List[str]:
            agent = agents.get(agent_id)
            if not agent:
                return []
            caps = agent.get("capabilities", [])
            if task_type in caps:
                return [agent_id]

            children = [
                a_id for a_id, a in agents.items()
                if a.get("parent_agent_id") == agent_id
            ]
            for child_id in children:
                chain = dfs(child_id)
                if chain:
                    return [agent_id] + chain
            return []

        return dfs(root_agent_id)