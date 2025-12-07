"""Shared dependencies for the API."""
from typing import Optional
from ..agents.orchestrator import AgentOrchestrator

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get the global orchestrator instance."""
    if orchestrator is None:
        raise RuntimeError("Orchestrator not initialized")
    return orchestrator


def set_orchestrator(orch: AgentOrchestrator) -> None:
    """Set the global orchestrator instance."""
    global orchestrator
    orchestrator = orch
