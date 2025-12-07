"""MCP (Model Context Protocol) tools integration."""
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server connection."""
    name: str
    transport: str = "stdio"  # stdio, sse, streamable-http
    command: Optional[str] = None
    args: List[str] = []
    url: Optional[str] = None
    env: Dict[str, str] = {}


class MCPToolset:
    """
    MCP toolset for integrating external MCP servers with the agent.

    This wraps the google.adk.tools.mcp_tool functionality with
    additional convenience methods.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._tools: List[Any] = []
        self._connected = False

    async def connect(self) -> bool:
        """Connect to the MCP server and discover tools."""
        try:
            from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
            from google.adk.tools.mcp_tool.mcp_session_manager import (
                StdioServerParameters,
                SseServerParameters,
            )

            if self.config.transport == "stdio":
                params = StdioServerParameters(
                    command=self.config.command,
                    args=self.config.args,
                    env=self.config.env or None,
                )
            elif self.config.transport == "sse":
                params = SseServerParameters(url=self.config.url)
            else:
                raise ValueError(f"Unsupported transport: {self.config.transport}")

            toolset = McpToolset(connection_params=params)
            self._tools = await toolset.get_tools()
            self._connected = True
            return True

        except ImportError:
            # Fallback if MCP not available
            self._connected = False
            return False
        except Exception as e:
            self._connected = False
            raise e

    @property
    def tools(self) -> List[Any]:
        """Get the discovered MCP tools."""
        return self._tools

    @property
    def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self._connected

    def get_tool_names(self) -> List[str]:
        """Get names of all available tools."""
        return [t.name for t in self._tools if hasattr(t, 'name')]


class MCPToolRegistry:
    """Registry for managing multiple MCP toolsets."""

    def __init__(self):
        self._toolsets: Dict[str, MCPToolset] = {}

    async def register(self, config: MCPServerConfig) -> MCPToolset:
        """Register and connect to an MCP server."""
        toolset = MCPToolset(config)
        await toolset.connect()
        self._toolsets[config.name] = toolset
        return toolset

    def get(self, name: str) -> Optional[MCPToolset]:
        """Get a registered toolset by name."""
        return self._toolsets.get(name)

    def all_tools(self) -> List[Any]:
        """Get all tools from all registered toolsets."""
        tools = []
        for toolset in self._toolsets.values():
            tools.extend(toolset.tools)
        return tools

    def list_servers(self) -> List[str]:
        """List all registered server names."""
        return list(self._toolsets.keys())


# Pre-configured MCP servers
COMMON_MCP_SERVERS = {
    "filesystem": MCPServerConfig(
        name="filesystem",
        transport="stdio",
        command="npx",
        args=["-y", "@anthropic/mcp-server-filesystem", "/"],
    ),
    "github": MCPServerConfig(
        name="github",
        transport="stdio",
        command="npx",
        args=["-y", "@anthropic/mcp-server-github"],
    ),
    "postgres": MCPServerConfig(
        name="postgres",
        transport="stdio",
        command="npx",
        args=["-y", "@anthropic/mcp-server-postgres"],
    ),
}


async def create_mcp_toolset(server_name: str) -> Optional[MCPToolset]:
    """Create a toolset for a common MCP server."""
    if server_name not in COMMON_MCP_SERVERS:
        return None

    config = COMMON_MCP_SERVERS[server_name]
    toolset = MCPToolset(config)
    await toolset.connect()
    return toolset
