"""Deterministic supervisor workflow for EV Market Intelligence."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from states.state import SupervisorState


logger = logging.getLogger(__name__)


_AGENT_FOCUS: Mapping[str, str] = {
    "market": "market demand, pricing, sales mix, and regional share dynamics",
    "policy": "major policy, regulatory, and incentive signals affecting EV adoption",
    "oem": "OEM strategies, product launches, and competitive positioning",
    "supply_chain": "battery, semiconductor, and drivetrain supply chain health",
    "finance": "funding flows, profitability, valuations, and capital market sentiment",
    "cross_layer_validation": "cross-checking analysis agent conclusions for consistency",
    "report_quality_check": "overall report structure, clarity, and completeness",
    "hallucination_check": "possible unsupported claims or hallucinations",
}


def _build_agent_message(agent_name: str, task_input: str) -> List[HumanMessage]:
    focus = _AGENT_FOCUS.get(
        agent_name,
        "your designated analysis scope",
    )
    content = (
        f"{task_input}\n\n"
        f"Provide findings covering {focus}."
        " Prioritise key metrics, actionable takeaways,"
        " and cite any assumptions you must make."
    )
    return [HumanMessage(content=content)]


def _summarise_agent_result(result: Any) -> str:
    """Best-effort extraction of printable content from LangGraph outputs."""

    if result is None:
        return "(no result)"
    if isinstance(result, str):
        return result
    if isinstance(result, Mapping):
        # LangGraph ReAct agents typically return {"messages": [...]}.
        messages = result.get("messages")
        if isinstance(messages, Sequence) and messages:
            last = messages[-1]
            try:
                return _summarise_agent_result(last)
            except Exception:  # pragma: no cover - defensive
                pass
        output = result.get("output")
        if output is not None:
            return _summarise_agent_result(output)
        return str(result)
    if hasattr(result, "content"):
        content = getattr(result, "content")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, Sequence):
            combined = "\n".join(str(part) for part in content if part)
            if combined:
                return combined
    if isinstance(result, Sequence):
        flattened = [item for item in result if item]
        if flattened:
            return _summarise_agent_result(flattened[-1])
    return str(result)


async def _invoke_agent(
    agent_name: str,
    agent: Any,
    task_input: str,
    state: SupervisorState,
    progress_handler: Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]] = None,
) -> str:
    """Run a single agent graph and record progress into state."""

    state.step(agent_name)  # guard against runaway loops
    logger.info("Running agent '%s' (step %d)", agent_name, state.total_steps)

    try:
        result = await agent.ainvoke({"messages": _build_agent_message(agent_name, task_input)})
    except Exception as exc:  # pragma: no cover - runtime safeguard
        state.retry_count += 1
        logger.exception("Agent '%s' failed: %s", agent_name, exc)
        raise

    summary = _summarise_agent_result(result)
    state.log(agent_name, summary)
    state.record_decision(summary)
    snapshot = state.snapshot(
        agent=agent_name,
        result={
            "summary": summary,
            "raw": result,
        },
    )

    if progress_handler is not None:
        maybe = progress_handler(snapshot)
        if asyncio.iscoroutine(maybe):
            await maybe

    return summary


def _compile_final_report(
    state: SupervisorState,
    analysis_order: Sequence[str],
    validation_order: Sequence[str],
) -> str:
    lines: List[str] = ["EV Market Supervisor Report", ""]

    if state.notes:
        def _append_section(title: str, agent_names: Sequence[str]) -> None:
            relevant = [(name, state.notes.get(name, [])) for name in agent_names]
            relevant = [(name, notes) for name, notes in relevant if notes]
            if not relevant:
                return
            lines.append(title)
            for name, notes in relevant:
                lines.append(f"- {name.replace('_', ' ').title()}: {notes[-1]}")
            lines.append("")

        _append_section("Analysis Highlights:", analysis_order)
        _append_section("Validation Findings:", validation_order)

    if state.decisions:
        lines.append("Logged Decisions:")
        for decision in state.decisions:
            lines.append(f"- {decision}")
        lines.append("")

    lines.append("Compiled automatically via deterministic supervisor flow.")
    return "\n".join(line for line in lines if line).strip()


def _update_stage(state: SupervisorState, stage: str) -> None:
    state.stage = stage
    logger.info("Supervisor stage advanced to '%s'", stage)


def build_supervisor_workflow(
    *,
    analysis_agents: Dict[str, Any],
    validation_agents: Dict[str, Any],
    supervisor_prompt: ChatPromptTemplate | str,
    llm: Any,
    supervisor_tools: Optional[Iterable[Any]] = None,
):
    """Return an async callable that runs agents sequentially."""

    del supervisor_prompt, llm, supervisor_tools  # handled inside individual agents

    analysis_order = list(analysis_agents.keys())
    validation_order = list(validation_agents.keys())

    async def run_supervisor(
        task_input: str,
        *,
        progress_handler: Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]] = None,
        recursion_limit: int = 75,
        state: Optional[SupervisorState] = None,
        **_: Any,
    ) -> SupervisorState:
        del recursion_limit  # deterministic flow ignores recursion
        supervisor_state = state or SupervisorState(task_input=task_input)
        logger.info(
            "Deterministic supervisor started for task '%s'", task_input
        )

        if analysis_order:
            _update_stage(supervisor_state, "analysis")
            for agent_name in analysis_order:
                agent = analysis_agents[agent_name]
                await _invoke_agent(
                    agent_name,
                    agent,
                    task_input,
                    supervisor_state,
                    progress_handler,
                )

        if validation_order:
            _update_stage(supervisor_state, "validation")
            for agent_name in validation_order:
                agent = validation_agents[agent_name]
                await _invoke_agent(
                    agent_name,
                    agent,
                    task_input,
                    supervisor_state,
                    progress_handler,
                )

        _update_stage(supervisor_state, "final")
        supervisor_state.final_report = _compile_final_report(
            supervisor_state,
            analysis_order,
            validation_order,
        )
        _update_stage(supervisor_state, "done")
        logger.info(
            "Deterministic supervisor completed after %d steps",
            supervisor_state.total_steps,
        )
        return supervisor_state

    return run_supervisor
