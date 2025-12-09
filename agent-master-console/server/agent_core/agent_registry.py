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

    def _iter_agent_files(self):
        for fname in os.listdir(self.base_path):
            if fname.endswith(".json"):
                yield os.path.join(self.base_path, fname)

    def list_agents(self) -> List[Dict[str, Any]]:
        agents = []
        for fpath in self._iter_agent_files():
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
        Update an existing agent configuration and persist it to disk.
        Uses dictionary access to avoid attribute errors.
        """
        agent = self.get_agent(agent_id)
        for key, value in updates.items():
            if key == "id":
                continue  # never allow id to change
            agent[key] = value
        agent["id"] = agent_id  # ensure id is preserved
        with open(self._agent_path(agent_id), "w", encoding="utf-8") as f:
            json.dump(agent, f, indent=2)
        return agent

    def _get_children(self, parent_agent_id: str) -> List[Dict[str, Any]]:
        children: List[Dict[str, Any]] = []
        for fpath in self._iter_agent_files():
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("parent_agent_id") == parent_agent_id:
                    children.append(data)
        return children

    def get_agent_tree(self, root_agent_id: str) -> Dict[str, Any]:
        """
        Build a simple parent/child tree starting at the given root.
        Uses dictionary keys (e.g. agent['id']) to avoid AttributeError.
        """
        root = self.get_agent(root_agent_id)

        def build(node: Dict[str, Any]) -> Dict[str, Any]:
            tree_node = {
                "id": node.get("id"),
                "name": node.get("name"),
                "model": node.get("model"),
                "system_prompt": node.get("system_prompt"),
                "tools": node.get("tools", []),
                "children": [],
            }
            for child in self._get_children(node.get("id")):
                tree_node["children"].append(build(child))
            return tree_node

        return build(root)

    def find_delegation_chain(self, task_type: str, root_agent_id: str) -> List[str]:
        """
        Return the delegation chain (by agent ids) for a task type starting from root.
        The search uses dictionary access for all agent data.
        """
        try:
            root = self.get_agent(root_agent_id)
        except FileNotFoundError:
            return []

        def matches(agent: Dict[str, Any]) -> bool:
            return (
                task_type == agent.get("agent_type")
                or task_type in agent.get("capabilities", [])
                or task_type in agent.get("specializations", [])
            )

        def dfs(agent: Dict[str, Any], path: List[str]) -> Optional[List[str]]:
            current_path = path + [agent.get("id")]
            if matches(agent):
                return current_path
            for child in self._get_children(agent.get("id")):
                chain = dfs(child, current_path)
                if chain:
                    return chain
            return None

        result = dfs(root, [])
        return result or []