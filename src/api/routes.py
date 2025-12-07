"""API routes for the AI Digital Assistant."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .server import get_orchestrator
from ..agents.orchestrator import AgentOrchestrator


router = APIRouter(tags=["agents"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    agent: str = "assistant"
    user_id: str = "default"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    agent: str


class AgentCreateRequest(BaseModel):
    """Request model for creating an agent."""
    name: str
    description: str
    instruction: str
    model: str = "gemini-2.5-flash"
    tools: List[str] = []


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str
    description: str
    model: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Send a message to an agent and get a response."""
    try:
        result = await orchestrator.run_agent(
            agent_name=request.agent,
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
        )
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            agent=request.agent,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[AgentInfo])
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """List all registered agents with metadata."""
    return orchestrator.list_agent_details()


@router.get("/agents/{name}", response_model=AgentInfo)
async def get_agent(
    name: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Get information about a specific agent."""
    agent = orchestrator.get_agent(name)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    return AgentInfo(
        name=agent.name,
        description=agent.description or "",
        model=getattr(agent, 'model', 'gemini-2.5-flash'),
    )


@router.post("/agents", response_model=AgentInfo)
async def create_agent(
    request: AgentCreateRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Create a new agent."""
    try:
        agent = orchestrator.create_agent(
            name=request.name,
            description=request.description,
            instruction=request.instruction,
            model=request.model,
        )
        return AgentInfo(
            name=agent.name,
            description=agent.description or "",
            model=request.model,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agents/parallel")
async def run_parallel(
    agent_messages: Dict[str, str],
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Run multiple agents in parallel."""
    try:
        results = await orchestrator.run_parallel(agent_messages)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-digital-assistant"}
