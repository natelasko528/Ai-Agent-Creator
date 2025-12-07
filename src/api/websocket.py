"""WebSocket support for real-time agent communication."""
import asyncio
import json
from typing import Dict, Set, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .server import get_orchestrator


ws_router = APIRouter()


class WebSocketManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to all connections for a user."""
        if user_id in self.active_connections:
            data = json.dumps(message)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(data)
                except Exception:
                    pass

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected users."""
        data = json.dumps(message)
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(data)
                except Exception:
                    pass


manager = WebSocketManager()


@ws_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time agent communication."""
    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process the message
            if message.get("type") == "chat":
                await handle_chat(websocket, user_id, message)
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
        manager.disconnect(websocket, user_id)


async def handle_chat(websocket: WebSocket, user_id: str, message: Dict[str, Any]):
    """Handle a chat message via WebSocket."""
    orchestrator = get_orchestrator()

    agent_name = message.get("agent", "assistant")
    user_message = message.get("message", "")
    session_id = message.get("session_id")

    # Send acknowledgment
    await websocket.send_text(json.dumps({
        "type": "ack",
        "message_id": message.get("id"),
    }))

    try:
        # Stream events from the agent
        if agent_name not in orchestrator._runners:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Agent '{agent_name}' not found",
            }))
            return

        runner = orchestrator._runners[agent_name]

        if session_id is None:
            session = await orchestrator._session_service.create_session(
                app_name="ai-assistant",
                user_id=user_id,
            )
            session_id = session.id

        # Send session info
        await websocket.send_text(json.dumps({
            "type": "session",
            "session_id": session_id,
        }))

        # Stream events
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            event_data = {
                "type": "event",
                "event_type": type(event).__name__,
            }

            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    text = ''.join(
                        p.text for p in event.content.parts
                        if hasattr(p, 'text')
                    )
                    if text:
                        event_data["content"] = text

            await websocket.send_text(json.dumps(event_data))

        # Send completion
        await websocket.send_text(json.dumps({
            "type": "complete",
            "session_id": session_id,
        }))

    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
        }))
