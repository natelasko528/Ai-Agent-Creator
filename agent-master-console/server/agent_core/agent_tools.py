from typing import List, Dict, Any

def get_tool_specs(tool_names: List[str]) -> List[Dict[str, Any]]:
    """
    Return OpenAI‑style tool schema for the requested tool names.
    Expand this function to add your own tools.
    """
    tool_specs: List[Dict[str, Any]] = []

    if "web_search" in tool_names:
        tool_specs.append({
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for up‑to‑date information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string."
                        }
                    },
                    "required": ["query"]
                },
            },
        })
    # Add additional tool definitions here
    return tool_specs
