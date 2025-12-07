"""FastAPI server for the AI Digital Assistant."""
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import router
from .websocket import ws_router
from ..agents.orchestrator import AgentOrchestrator


# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    orchestrator = AgentOrchestrator()

    # Register default agents
    from ..tools.code_tools import read_file, write_file, edit_file, run_code
    from ..tools.mcp_tools import MCPToolRegistry, COMMON_MCP_SERVERS
    from google.adk.tools import FunctionTool

    # Build a comprehensive tool suite (Gemini ADK HEK/AGK friendly)
    tool_registry = MCPToolRegistry()
    for config in COMMON_MCP_SERVERS.values():
        try:
            # Best-effort connect; failures simply skip MCP extras
            await tool_registry.register(config)
        except Exception:
            continue

    code_tools = [
        FunctionTool(func=read_file),
        FunctionTool(func=write_file),
        FunctionTool(func=edit_file),
        FunctionTool(func=run_code),
    ]
    unified_tools = code_tools + tool_registry.all_tools()

    orchestrator.create_agent(
        name="assistant",
        description="Main AI assistant for orchestrating agents and delegating tasks",
        instruction="""You are a helpful AI assistant with access to a rich tool suite. Plan, delegate, and synthesize outcomes.
        Keep explanations concise but clear.""",
        tools=unified_tools,
        model="gemini-3.0-pro",
    )

    orchestrator.create_agent(
        name="planner",
        description="Strategic planner for breaking down complex projects",
        instruction="""You are a senior strategist. Create crisp plans, milestones, and dependencies before execution. Validate scope
        and surface risks before proceeding.""",
        tools=unified_tools,
        model="gemini-3.0-pro",
    )

    orchestrator.create_agent(
        name="executor",
        description="Precision execution agent for coding and operational tasks",
        instruction="""You turn plans into reality with meticulous execution. Write and refine code, run experiments, and return
        tested outcomes with logs and diffs.""",
        tools=unified_tools,
        model="gemini-2.5-pro",
    )

    orchestrator.create_agent(
        name="research",
        description="Fast research and reconnaissance agent",
        instruction="""You synthesize information quickly, highlight citations when possible, and share concise briefs with key
        signals and open questions.""",
        tools=unified_tools,
        model="gemini-2.5-flash",
    )

    yield

    # Cleanup
    orchestrator = None


def create_api() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Digital Assistant",
        description="Professional AI agent orchestration system with Gemini ADK",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router, prefix="/api")
    app.include_router(ws_router)

    # Serve static files (GUI)
    static_path = Path(__file__).parent.parent / "gui" / "dist"
    if static_path.exists():
        app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    return app


def get_orchestrator() -> AgentOrchestrator:
    """Get the global orchestrator instance."""
    if orchestrator is None:
        raise RuntimeError("Orchestrator not initialized")
    return orchestrator
