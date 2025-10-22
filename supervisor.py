"""Supervisor graph assembly for the EV Market Intelligence system."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from langgraph.constants import END
from langgraph.graph import CompiledStateGraph, StateGraph
from langgraph.prebuilt import create_supervisor

from .agents import build_analysis_agents, build_validation_agents
from .prompts import SUPERVISOR_INSTRUCTIONS
from .state import AgentName, GraphState, SupervisorState

SUPERVISOR_NODE_NAME = "supervisor"


def build_supervisor_graph(
    llm: Any,
    *,
    analysis_tools: Optional[Iterable[Any]] = None,
    validation_tools: Optional[Iterable[Any]] = None,
    supervisor_tools: Optional[Iterable[Any]] = None,
    max_retries: int = 2,
    max_total_steps: int = 25,
) -> CompiledStateGraph:
    """Create the supervisor-centric LangGraph workflow.

    Parameters
    ----------
    llm:
        Backing large language model client compatible with LangChain/ LangGraph.
    analysis_tools:
        Optional iterable of tool callables shared by the analysis agents.
    validation_tools:
        Optional iterable of tool callables shared by the validation agents.
    supervisor_tools:
        Optional iterable of tools exposed to the supervisor (e.g., logging).
    max_retries:
        Maximum retries per agent before the supervisor aborts.
    max_total_steps:
        Upper bound on total graph iterations to avoid infinite loops.
    """

    analysis_agents = build_analysis_agents(llm=llm, tools=analysis_tools)
    validation_agents = build_validation_agents(llm=llm, tools=validation_tools)

    members: Dict[AgentName, Any] = {
        **analysis_agents,
        **validation_agents,
    }

    supervisor = create_supervisor(
        llm=llm,
        members=list(members.keys()),
        prompt=SUPERVISOR_INSTRUCTIONS,
        tools=list(supervisor_tools or []),
    )

    workflow: StateGraph[GraphState] = StateGraph(GraphState)

    workflow.add_node(
        SUPERVISOR_NODE_NAME,
        _make_supervisor_node(supervisor, max_retries=max_retries, max_total_steps=max_total_steps),
    )

    for name, node in members.items():
        workflow.add_node(name, _wrap_agent_node(name, node))
        workflow.add_edge(name, SUPERVISOR_NODE_NAME)
    workflow.add_conditional_edges(
        SUPERVISOR_NODE_NAME,
        _route_from_supervisor,
        {name: name for name in members.keys()},
        default=END,
    )
    workflow.set_entry_point(SUPERVISOR_NODE_NAME)

    return workflow.compile()


def _make_supervisor_node(
    supervisor_runnable: Any,
    *,
    max_retries: int,
    max_total_steps: int,
):
    """Wrap the supervisor runnable with shared state initialization and guards."""

    def node(state: GraphState) -> GraphState:
        supervisor_state = state.get("supervisor_state")
        if supervisor_state is None:
            task_input = state.get("task_input", "")
            supervisor_state = SupervisorState(
                task_input=task_input,
                max_retries=max_retries,
                max_total_steps=max_total_steps,
            )
            state["supervisor_state"] = supervisor_state

        supervisor_state.check_loop_safeguards()

        decision = supervisor_runnable.invoke(state)
        next_step = decision.get("next")
        if next_step is None:
            raise RuntimeError(
                "Supervisor did not emit a 'next' route. Implement routing in your prompt or custom parser."
            )

        supervisor_state.decisions.append(decision.get("reasoning", ""))
        state["last_agent"] = next_step
        state["next_agent"] = next_step

        return state

    return node


def _wrap_agent_node(agent_name: AgentName, runnable: Any):
    """Attach bookkeeping hooks to each agent runnable."""

    def node(state: GraphState) -> GraphState:
        supervisor_state = state["supervisor_state"]
        supervisor_state.register_step(agent_name)
        supervisor_state.check_loop_safeguards()

        # Call into the actual agent runnable.
        result = runnable.invoke(state)
        output_text = result.get("content", "") if isinstance(result, dict) else str(result)

        supervisor_state.mark_agent_result(agent_name, "succeeded", output_text)
        supervisor_state.reset_agent_retry(agent_name)

        state.update(result if isinstance(result, dict) else {f"{agent_name}_result": result})
        return state

    return node


def _route_from_supervisor(state: GraphState) -> str:
    """Return the next node label selected by the supervisor."""

    next_agent = state.get("next_agent")
    if next_agent is None:
        return END
    return next_agent
