import os
from typing import List

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


app = FastAPI(title="Agent Master Console API")

registry = AgentRegistry()
runtime = AgentRuntime(registry)

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

env_origins = os.getenv("ALLOWED_ORIGINS")
allow_origins = (
    [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    if env_origins
    else default_origins
)

allow_credentials = "*" not in allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
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
