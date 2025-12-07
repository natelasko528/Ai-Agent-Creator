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
    from google.adk.tools import FunctionTool

    code_tools = [
        FunctionTool(func=read_file),
        FunctionTool(func=write_file),
        FunctionTool(func=edit_file),
        FunctionTool(func=run_code),
    ]

    orchestrator.create_agent(
        name="assistant",
        description="Main AI assistant for general tasks",
        instruction="""You are a helpful AI assistant with access to code editing and execution tools.
        Help users with their tasks efficiently and accurately.""",
        tools=code_tools,
    )

    orchestrator.create_agent(
        name="coder",
        description="Specialized coding assistant",
        instruction="""You are an expert programmer. Write clean, efficient, well-documented code.
        Use the provided tools to read, edit, and run code.""",
        tools=code_tools,
        model="gemini-2.5-pro",
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
