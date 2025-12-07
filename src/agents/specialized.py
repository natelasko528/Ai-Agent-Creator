"""Specialized agents for specific tasks."""
from typing import Any, Dict, List, Optional
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .base import BaseAgent, AgentConfig, LLMAgentWrapper


# Code Agent - for code editing and execution
CODE_AGENT_INSTRUCTION = """You are an expert code assistant with full capabilities to:
1. Read, analyze, and understand code in any programming language
2. Write new code with best practices and clean architecture
3. Edit existing code with precise modifications
4. Execute code safely and report results
5. Debug issues and suggest fixes

Always:
- Explain your reasoning before making changes
- Use proper error handling
- Follow language-specific conventions
- Test changes when possible
"""


class CodeAgent(LLMAgentWrapper):
    """Agent specialized for code editing and execution."""

    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        tools: List[Any] = None,
    ):
        config = AgentConfig(
            name="code_agent",
            description="Expert code assistant for editing, running, and debugging code",
            instruction=CODE_AGENT_INSTRUCTION,
            model=model,
            tools=tools or [],
        )
        super().__init__(config)


# Research Agent - for information gathering
RESEARCH_AGENT_INSTRUCTION = """You are an expert research assistant capable of:
1. Searching for and gathering information from multiple sources
2. Analyzing and synthesizing complex information
3. Providing accurate, well-sourced answers
4. Identifying key insights and patterns

Always:
- Cite your sources when possible
- Distinguish between facts and opinions
- Acknowledge uncertainty
- Provide comprehensive yet concise answers
"""


class ResearchAgent(LLMAgentWrapper):
    """Agent specialized for research and information gathering."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        tools: List[Any] = None,
    ):
        config = AgentConfig(
            name="research_agent",
            description="Research assistant for gathering and analyzing information",
            instruction=RESEARCH_AGENT_INSTRUCTION,
            model=model,
            tools=tools or [],
        )
        super().__init__(config)


# Task Agent - for general task execution
TASK_AGENT_INSTRUCTION = """You are a versatile task execution agent capable of:
1. Breaking down complex tasks into manageable steps
2. Executing tasks efficiently and accurately
3. Coordinating with other agents when needed
4. Tracking progress and reporting status

Always:
- Plan before acting
- Validate inputs and outputs
- Handle errors gracefully
- Provide clear status updates
"""


class TaskAgent(LLMAgentWrapper):
    """Agent specialized for general task execution."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        tools: List[Any] = None,
    ):
        config = AgentConfig(
            name="task_agent",
            description="General-purpose task execution agent",
            instruction=TASK_AGENT_INSTRUCTION,
            model=model,
            tools=tools or [],
        )
        super().__init__(config)


def create_specialized_agent(
    agent_type: str,
    model: str = None,
    tools: List[Any] = None,
) -> BaseAgent:
    """Factory function to create specialized agents."""
    agents = {
        "code": CodeAgent,
        "research": ResearchAgent,
        "task": TaskAgent,
    }

    if agent_type not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}")

    kwargs = {}
    if model:
        kwargs["model"] = model
    if tools:
        kwargs["tools"] = tools

    return agents[agent_type](**kwargs)
