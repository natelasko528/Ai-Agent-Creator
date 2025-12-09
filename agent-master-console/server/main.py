from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr

from agent_core.agent_registry import AgentRegistry
from agent_core.agent_runtime import AgentRuntime


class AgentCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    model: constr(min_length=1) = "gpt-4.1-mini"
    system_prompt: constr(min_length=1) = "You are a helpful assistant."
    tools: List[constr(min_length=1)] = Field(default_factory=list)


class Agent(AgentCreate):
    id: str
    parent_agent_id: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    model: Optional[constr(min_length=1)] = None
    system_prompt: Optional[constr(min_length=1)] = None
    tools: Optional[List[constr(min_length=1)]] = None
    parent_agent_id: Optional[str] = None
    capabilities: Optional[List[str]] = None
    specializations: Optional[List[str]] = None


app = FastAPI(title="Agent Master Console API")

registry = AgentRegistry()
runtime = AgentRuntime(registry)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/agents", response_model=List[Agent])
def list_agents():
    return registry.list_agents()


@app.post("/agents", response_model=Agent, status_code=201)
def create_agent(config: AgentCreate):
    return registry.create_agent(config.model_dump())


@app.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: str):
    try:
        return registry.get_agent(agent_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.put("/agents/{agent_id}", response_model=Agent)
def update_agent(agent_id: str, updates: AgentUpdate):
    """
    Update an agent and return the updated agent record.
    """
    try:
        updated = registry.update_agent(
            agent_id,
            {k: v for k, v in updates.model_dump(exclude_none=True).items()},
        )
        return updated
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.websocket("/ws/{agent_id}")
async def chat_socket(ws: WebSocket, agent_id: str):
    await ws.accept()
    session_id = f"ws-{id(ws)}"
    try:
        registry.get_agent(agent_id)
    except FileNotFoundError as exc:
        await ws.close(code=4404, reason=str(exc))
        return

    try:
        while True:
            user_msg = await ws.receive_text()
            async for chunk in runtime.generate(agent_id, user_msg, session_id=session_id):
                await ws.send_text(chunk)
    except WebSocketDisconnect:
        return
    except FileNotFoundError as exc:
        await ws.close(code=4404, reason=str(exc))
    finally:
        runtime.close_session(session_id)
