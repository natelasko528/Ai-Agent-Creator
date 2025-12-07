"""Vercel serverless entry point for the AI Digital Assistant API."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Simple API for Vercel serverless
app = FastAPI(title="AI Digital Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "ai-digital-assistant"}


@app.get("/api/agents")
async def list_agents():
    return ["assistant", "coder"]


@app.get("/api/agents/{name}")
async def get_agent(name: str):
    agents = {
        "assistant": {
            "name": "assistant",
            "description": "Main AI assistant for general tasks",
            "model": "gemini-2.5-flash"
        },
        "coder": {
            "name": "coder",
            "description": "Specialized coding assistant",
            "model": "gemini-2.5-pro"
        }
    }
    return agents.get(name, {"error": "Agent not found"})


# Vercel handler
handler = Mangum(app, lifespan="off")
