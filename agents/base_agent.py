from __future__ import annotations
from typing import Any, Sequence, Callable
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool


def build_base_agent(
    *,
    name: str,
    system_prompt: str,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    model: str | Any = "gpt-4o-mini",
    temperature: float = 0.2,
    debug: bool = False,
):
    """
    Build a simple agent node for Supervisor-managed multi-agent workflows.

    Parameters
    ----------
    name : str
        Agent identifier used by the Supervisor.
    system_prompt : str
        System-level description of the agent's analytical role.
    tools : list, optional
        Tool functions or BaseTool objects accessible to this agent.
    model : str or ChatModel, default "gpt-4o-mini"
        The underlying LLM model (can be passed as string or pre-initialized object).
    temperature : float, default 0.2
        Sampling temperature for deterministic responses.
    debug : bool, default False
        Whether to enable verbose execution tracing.

    Returns
    -------
    agent : LangGraph Agent (Runnable)
        A runnable agent node compatible with `create_supervisor`.
    """

    # Ensure model object is ChatModel
    llm = model if not isinstance(model, str) else ChatOpenAI(model=model, temperature=temperature)

    # Supervisor context에서는 다음 인자만 유효:
    # - model (필수)
    # - tools (도구)
    # - system_prompt (에이전트 역할 정의)
    # - name (Supervisor routing에 필요)
    # - debug (로깅용)
    agent = create_agent(
        model=llm,
        tools=tools or [],
        system_prompt=system_prompt,
        name=name,
        debug=debug,
    )

    return agent
