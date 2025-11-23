# Agent Master Console

This repository contains a simple full‑stack application for managing and chatting with AI agents using the OpenAI Agents SDK.  It consists of a FastAPI backend and a React frontend styled like the ChatGPT interface.  You can create agents, configure their models, prompts, and tools, and chat with each agent in a dedicated chat window.

## Features

- **Create and manage multiple agents.** Each agent has its own name, model, system prompt, and tool configuration.
- **Chat with agents in real time.** The frontend uses WebSockets to stream messages from the backend as the agent responds.
- **Persistent registry.** Agents are stored as JSON files in the `server/agent_core/templates` directory.
- **Extensible tools.** You can add custom tools to `server/agent_core/agent_tools.py` to expose functionality to the agents.

## Getting started

### Backend setup

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# set your OpenAI API key
export OPENAI_API_KEY="sk-..."

uvicorn main:app --reload
```

### Frontend setup

```bash
cd client
npm install
npm run dev
```

The backend will run on `http://localhost:8000` and the frontend on `http://localhost:5173`.

### Running tests

This repository includes a simple E2E test in `server/tests/test_e2e_live.py`.  To run the tests, make sure your OpenAI API key is set and then execute:

```bash
cd server
pytest
```

The test creates an agent, lists agents, and sends a message over WebSockets to ensure the flow works end to end.
This directory contains the primary files for the Agent Master Console. See individual subdirectories for details and usage.
