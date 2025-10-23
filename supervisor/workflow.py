"""Deterministic supervisor workflow for EV Market Intelligence."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import re

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from states.state import SupervisorState


logger = logging.getLogger(__name__)


_AGENT_FOCUS: Mapping[str, str] = {
    "finance_agent": "capital markets, funding flows, stock movements, and profitability indicators",
    "market_agent": "market demand, pricing, sales mix, and regional share dynamics",
    "policy_agent": "major policy, regulatory, and incentive signals affecting EV adoption",
    "oem_agent": "OEM strategies, product launches, and competitive positioning",
    "supply_agent": "battery, semiconductor, and drivetrain supply chain health",
    "cross_agent": "cross-checking analysis agent conclusions for consistency",
    "report_agent": "overall report structure, clarity, and completeness",
    "hallu_agent": "possible unsupported claims or hallucinations",
}


def _build_agent_message(agent_name: str, task_input: str) -> List[HumanMessage]:
    focus = _AGENT_FOCUS.get(
        agent_name,
        "your designated analysis scope",
    )
    content = (
        f"{task_input}\n\n"
        f"Focus on: {focus}\n"
        f"Provide key facts in 6 sentences or less in Korean. Include only essential metrics and insights. "
        f"Mention assumptions or risks concisely if necessary."
    )
    if agent_name == "oem_agent":
        content += " Include at least two URLs from recent relevant news after the Korean explanation."
    return [HumanMessage(content=content)]


def _summarise_agent_result(result: Any) -> str:
    """Extract printable content from LangGraph outputs."""

    if result is None:
        return "(no result)"
    if isinstance(result, str):
        return result
    if isinstance(result, Mapping):
        messages = result.get("messages")
        if isinstance(messages, Sequence) and messages:
            last = messages[-1]
            try:
                return _summarise_agent_result(last)
            except Exception:
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
    """Run a single agent and record progress into state."""

    state.step(agent_name)
    logger.info("Running agent '%s' (step %d)", agent_name, state.total_steps)

    try:
        result = await agent.ainvoke({"messages": _build_agent_message(agent_name, task_input)})
    except Exception as exc:
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
    state.add_to_history(snapshot)

    if progress_handler is not None:
        maybe = progress_handler(snapshot)
        if asyncio.iscoroutine(maybe):
            await maybe

    return summary


def _clean_text(value: str, *, sentence_limit: int = 4) -> str:
    if not isinstance(value, str):
        value = str(value)
    text = re.sub(r"`+", "", value)
    text = re.sub(r"^\s*#+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\*\-•]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "데이터가 충분하지 않습니다."
    sentences = re.split(r"(?<=[.!?\.])\s+", text)
    trimmed = " ".join(sentences[:sentence_limit]).strip()
    return trimmed or "데이터가 충분하지 않습니다."


def _compile_final_report(
    state: SupervisorState,
    analysis_order: Sequence[str],
    validation_order: Sequence[str],
) -> str:
    def _latest(agent: str) -> str:
        notes = state.notes.get(agent, [])
        if not notes:
            return "데이터가 충분하지 않습니다."
        return _clean_text(notes[-1])

    def _indent(lines: Sequence[str]) -> List[str]:
        return [f"   - {line}" for line in lines if line]

    def _combine_agents(agents: Sequence[str]) -> str:
        snippets = [
            _latest(agent)
            for agent in agents
            if state.notes.get(agent)
        ]
        unique: list[str] = []
        seen: set[str] = set()
        for snippet in snippets:
            if snippet not in seen:
                unique.append(snippet)
                seen.add(snippet)
        return " ".join(unique) if unique else "데이터가 충분하지 않습니다."

    def _extract_references() -> List[str]:
        refs: set[str] = set()

        def _collect_from_text(text: str) -> None:
            for match in re.findall(r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+", text):
                refs.add(match.rstrip(".,;"))

        for notes in state.notes.values():
            for note in notes:
                _collect_from_text(note)

        for entry in state.history:
            raw = entry.get("result", {}).get("raw")

            def _visit(value: Any) -> None:
                if isinstance(value, str):
                    _collect_from_text(value)
                    return
                if isinstance(value, Mapping):
                    for item in value.values():
                        _visit(item)
                elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                    for item in value:
                        _visit(item)

            _visit(raw)

        return sorted(refs)

    exec_summary = [
        f"User Query: {_clean_text(state.task_input, sentence_limit=1)}",
        f"Key Finding: {_latest('market_agent')}",
        f"Finance Metrics: {_latest('finance_agent')}",
        "Action: Review policy and supply chain risks to establish execution plan.",
    ]

    market_section = _combine_agents(["market_agent", "policy_agent"])
    policy_section = _latest("policy_agent")
    oem_section = _latest("oem_agent")
    supply_section = _latest("supply_agent")
    finance_section = _latest("finance_agent")
    cross_section = _combine_agents(validation_order)

    references = _extract_references()
    if not references:
        references = ["No external sources cited. Review agent notes for additional information."]

    lines: List[str] = [
        "1. EXECUTIVE SUMMARY",
        *_indent(exec_summary),
        "",
        "2. MARKET OVERVIEW",
        *_indent([
            "Global and Regional Trends:",
            market_section,
        ]),
        "",
        "3. POLICY/REGULATION",
        *_indent([policy_section]),
        "",
        "4. OEM ANALYSIS",
        *_indent([oem_section]),
        "",
        "5. SUPPLY CHAIN ANALYSIS",
        *_indent([supply_section]),
        "",
        "6. FINANCIAL OUTLOOK",
        *_indent([finance_section]),
        "",
        "7. CROSS-LAYER INSIGHTS",
        *_indent([cross_section]),
        "",
        "8. REFERENCES",
        *_indent(references),
        "",
        "Report auto-generated by EV Market Supervisor pipeline.",
    ]

    return "\n".join(line for line in lines if line is not None).strip()


def _update_stage(state: SupervisorState, stage: str) -> None:
    state.stage = stage
    logger.info("Supervisor stage advanced to '%s'", stage)


def build_supervisor_workflow(
    *,
    analysis_agents: Dict[str, Any],
    validation_agents: Dict[str, Any],
    supervisor_prompt: Optional[ChatPromptTemplate | str] = None,
    llm: Optional[Any] = None,
    supervisor_tools: Optional[Iterable[Any]] = None,
):
    """Return an async callable that runs agents sequentially."""

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
