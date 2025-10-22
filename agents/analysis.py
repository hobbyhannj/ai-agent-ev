"""Builders for analysis agents managed by the supervisor."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from langgraph.prebuilt import create_react_agent

from ..prompts import get_analysis_prompt
from ..state import AnalysisAgentName

ANALYSIS_AGENT_SEQUENCE: Iterable[AnalysisAgentName] = (
    "market",
    "policy",
    "oem",
    "supply_chain",
    "finance",
)


def build_analysis_agents(
    llm: Any,
    tools: Optional[Iterable[Any]] = None,
    overrides: Optional[Dict[AnalysisAgentName, str]] = None,
) -> Dict[AnalysisAgentName, Any]:
    """Create ReAct-style agents for each analysis role."""

    agents: Dict[AnalysisAgentName, Any] = {}
    overrides = overrides or {}

    for name in ANALYSIS_AGENT_SEQUENCE:
        prompt = overrides.get(name, get_analysis_prompt(name))
        agent = create_react_agent(
            llm=llm,
            tools=list(tools or []),
            prompt=prompt,
        )
        agents[name] = agent

    return agents
