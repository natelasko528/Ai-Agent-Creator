from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from agent_core.agent_registry import AgentRegistry
from agent_core.agent_runtime import AgentRuntime

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

@app.get("/agents")
def list_agents():
    return registry.list_agents()

@app.post("/agents")
def create_agent(config: dict):
    return registry.create_agent(config)

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    return registry.get_agent(agent_id)

@app.websocket("/ws/{agent_id}")
async def chat_socket(ws: WebSocket, agent_id: str):
    await ws.accept()
    session_id = f"ws-{id(ws)}"
    try:
        while True:
            user_msg = await ws.receive_text()
            async for chunk in runtime.generate(agent_id, user_msg, session_id=session_id):
                await ws.send_text(chunk)
    except WebSocketDisconnect:
        runtime.close_session(session_id)
        return