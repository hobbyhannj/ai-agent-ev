"""Builders for validation agents managed by the supervisor."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from langgraph.prebuilt import create_react_agent

from ..prompts import get_validation_prompt
from ..state import ValidationAgentName

VALIDATION_AGENT_SEQUENCE: Iterable[ValidationAgentName] = (
    "cross_layer_validation",
    "report_quality_check",
    "hallucination_check",
)


def build_validation_agents(
    llm: Any,
    tools: Optional[Iterable[Any]] = None,
    overrides: Optional[Dict[ValidationAgentName, str]] = None,
) -> Dict[ValidationAgentName, Any]:
    """Create ReAct agents for each validation role."""

    agents: Dict[ValidationAgentName, Any] = {}
    overrides = overrides or {}

    for name in VALIDATION_AGENT_SEQUENCE:
        prompt = overrides.get(name, get_validation_prompt(name))
        agent = create_react_agent(
            llm=llm,
            tools=list(tools or []),
            prompt=prompt,
        )
        agents[name] = agent

    return agents
