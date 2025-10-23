"""
File: builder.py
Author: 한정석
Date: 2025. 10. 23.
Last Modified: 2025. 10. 23.
Description:
    - Build and compile the EV Market Intelligence Supervisor workflow.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from supervisor.prompt import SUPERVISOR_PROMPT


def build_supervisor_workflow(
    *,
    analysis_agents: Dict[str, Any],
    validation_agents: Optional[Dict[str, Any]] = None,
    llm: Any | None = None,
    llm_model: str = "gpt-4o",
    supervisor_tools: Optional[list[Any]] = None,
):
    """
    Construct a LangGraph supervisor workflow that orchestrates analysis agents.

    Parameters
    ----------
    analysis_agents : dict[str, Any]
        Mapping of agent_name → agent runnable
    validation_agents : dict[str, Any], optional
        Additional validator agents (default = None)
    llm : ChatOpenAI, optional
        Pre-initialized LLM object for supervisor coordination
    llm_model : str, optional
        Model name (only used if `llm` is not provided)
    supervisor_tools : list, optional
        Optional shared tools available to the supervisor

    Returns
    -------
    compiled_workflow : langgraph.graph.CompiledStateGraph
        A compiled, runnable supervisor workflow.
    """

    if llm is None:
        llm = ChatOpenAI(model=llm_model, temperature=0.2)

    members: Dict[str, Any] = {**analysis_agents}
    if validation_agents:
        members.update(validation_agents)

    supervisor = create_supervisor(
        agents=list(members.values()),      # 실제 runnable
        model=llm,                          # Supervisor LLM
        prompt=SUPERVISOR_PROMPT,           # MessagesPlaceholder 기반 Prompt
        tools=supervisor_tools or [],       # Supervisor 전용 도구
        include_agent_name="inline",        # Agent 이름을 명시적으로 포함시킴
    )

    return supervisor.compile()
