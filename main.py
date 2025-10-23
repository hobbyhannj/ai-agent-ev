"""Entry point for assembling and running the EV Market Supervisor workflow."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

from langchain_openai import ChatOpenAI

from agents import build_analysis_agents, build_validation_agents
from supervisor.builder import build_supervisor_workflow
from templates import (
    CROSS_LAYER_VALIDATION_PROMPT,
    FINANCE_PROMPT,
    HALLUCINATION_CHECK_PROMPT,
    MARKET_PROMPT,
    OEM_PROMPT,
    POLICY_PROMPT,
    REPORT_QUALITY_CHECK_PROMPT,
    SUPERVISOR_PROMPT,
    SUPPLY_CHAIN_PROMPT,
)
from tools import get_analysis_tools, get_validation_tools
from states.state import SupervisorState


logger = logging.getLogger(__name__)


@dataclass
class PromptLookup:
    """Minimal helper that offers a `.render(name)` interface."""

    mapping: Mapping[str, Any]

    def render(self, agent_name: str) -> Any:
        return self.mapping[agent_name]


def _build_analysis_prompt_lookup() -> PromptLookup:
    prompts: Dict[str, Any] = {
        "market": MARKET_PROMPT,
        "policy": POLICY_PROMPT,
        "oem": OEM_PROMPT,
        "supply_chain": SUPPLY_CHAIN_PROMPT,
        "finance": FINANCE_PROMPT,
    }
    return PromptLookup(prompts)


def _build_validation_prompt_lookup() -> PromptLookup:
    prompts: Dict[str, Any] = {
        "cross_layer_validation": CROSS_LAYER_VALIDATION_PROMPT,
        "report_quality_check": REPORT_QUALITY_CHECK_PROMPT,
        "hallucination_check": HALLUCINATION_CHECK_PROMPT,
    }
    return PromptLookup(prompts)


def build_workflow(
    llm: Any,
    *,
    supervisor_tools: Optional[Iterable[Any]] = None,
    enable_tools: bool = True,
) -> Any:
    """Configure the agents, tools, and supervisor loop for a supplied LLM."""

    analysis_prompts = _build_analysis_prompt_lookup()
    validation_prompts = _build_validation_prompt_lookup()

    analysis_tools = get_analysis_tools() if enable_tools else {}
    validation_tools = get_validation_tools() if enable_tools else {}

    logger.info(
        "Building workflow with %d analysis tools and %d validation tools (tools enabled=%s)",
        len(analysis_tools),
        len(validation_tools),
        enable_tools,
    )

    analysis_agents = build_analysis_agents(llm, analysis_prompts, analysis_tools)
    validation_agents = build_validation_agents(llm, validation_prompts, validation_tools)

    workflow = build_supervisor_workflow(
        llm=llm,
        analysis_agents=analysis_agents,
        validation_agents=validation_agents,
        supervisor_prompt=SUPERVISOR_PROMPT,
        supervisor_tools=list(supervisor_tools or []),
    )

    return workflow


async def run_supervisor_task(
    task_input: str,
    *,
    llm: Any | None = None,
    supervisor_tools: Optional[Iterable[Any]] = None,
    enable_tools: bool = True,
    recursion_limit: int = 75,
) -> str:
    """Build the workflow (if needed) and return the supervisor's final report."""

    logger.info("Starting supervisor task for instruction: %s", task_input)
    state = await run_supervisor_state(
        task_input,
        llm=llm,
        supervisor_tools=supervisor_tools,
        enable_tools=enable_tools,
        recursion_limit=recursion_limit,
    )
    logger.info("Supervisor task completed with final report length %d", len(state.final_report or ""))
    return state.final_report


async def run_supervisor_state(
    task_input: str,
    *,
    llm: Any | None = None,
    supervisor_tools: Optional[Iterable[Any]] = None,
    enable_tools: bool = True,
    progress_handler: Optional[Callable[[Dict[str, Any]], Any]] = None,
    recursion_limit: int = 75,
) -> SupervisorState:
    """Build the workflow and return the full supervisor state for a task."""

    llm_instance = llm or _build_default_llm()
    if llm is None:
        logger.info("No LLM provided; constructed default client %s", llm_instance)
    else:
        logger.info("Running supervisor state with provided LLM %s", llm_instance)
    workflow = build_workflow(
        llm_instance,
        supervisor_tools=supervisor_tools,
        enable_tools=enable_tools,
    )
    logger.info("Invoking workflow with recursion limit %d", recursion_limit)
    return await workflow(
        task_input,
        progress_handler=progress_handler,
        recursion_limit=recursion_limit,
    )


def _build_default_llm() -> ChatOpenAI:
    """Construct a default ChatOpenAI client from environment variables."""

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    logger.info("Creating ChatOpenAI client with model=%s temperature=%s", model, temperature)
    return ChatOpenAI(model=model, temperature=temperature)


def _parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the EV Market Supervisor workflow.")
    parser.add_argument("task", help="High-level instruction for the supervisor to execute.")
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="Model name for ChatOpenAI (defaults to env OPENAI_MODEL or gpt-4o-mini).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.getenv("OPENAI_TEMPERATURE", "0")),
        help="Sampling temperature for the model (defaults to env OPENAI_TEMPERATURE or 0).",
    )
    parser.add_argument(
        "--disable-tools",
        action="store_true",
        help="Run agents without calling auxiliary tools (defaults to use tools).",
    )
    parser.add_argument(
        "--recursion-limit",
        type=int,
        default=75,
        help="Maximum LangGraph recursion depth before aborting (default: 75).",
    )
    return parser.parse_args()


def _build_cli_llm(model: str, temperature: float) -> ChatOpenAI:
    return ChatOpenAI(model=model, temperature=temperature)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = _parse_cli_args()
    logger.info(
        "CLI invocation with model=%s temperature=%s enable_tools=%s recursion_limit=%d",
        args.model,
        args.temperature,
        not args.disable_tools,
        args.recursion_limit,
    )
    llm = _build_cli_llm(args.model, args.temperature)
    logger.info("Constructed CLI LLM client: %s", llm)
    final_report = asyncio.run(
        run_supervisor_task(
            args.task,
            llm=llm,
            enable_tools=not args.disable_tools,
            recursion_limit=args.recursion_limit,
        )
    )
    print("\n=== Final Report ===\n")
    print(final_report)


__all__ = ["build_workflow", "run_supervisor_task", "run_supervisor_state"]


if __name__ == "__main__":
    main()
