"""Entry point for assembling and running the EV Market Supervisor workflow."""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

import requests

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


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
    parser.add_argument(
        "--print-server-url",
        default=os.getenv("PDF_SERVICE_URL", "http://127.0.0.1:8080"),
        help="Base URL for the PDF rendering service (default: http://127.0.0.1:8080).",
    )
    parser.add_argument(
        "--pdf-output",
        type=Path,
        help="If provided, save the final report as a PDF at the given path via the print service.",
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
    if args.pdf_output:
        plan = _generate_document_plan(llm, args.task, final_report)
        charts = _build_chart_images(plan.get("charts", []))
        _export_pdf(
            final_report,
            output_path=args.pdf_output,
            base_url=args.print_server_url,
            metadata=plan,
            charts=charts,
        )


def _export_pdf(
    report_text: str,
    *,
    output_path: Path,
    base_url: str,
    metadata: Dict[str, Any],
    charts: List[Dict[str, Any]],
) -> None:
    output_path = output_path.expanduser().resolve()
    if not report_text.strip():
        logger.warning("Skipping PDF export because the final report is empty.")
        return

    payload: Dict[str, Any] = {
        "report": report_text,
        "title": metadata.get("title") or "EV Market Supervisor Report",
        "subtitle": metadata.get("subtitle"),
        "summary": metadata.get("summary"),
        "prepared_for": metadata.get("prepared_for"),
        "prepared_by": metadata.get("prepared_by") or "EV Market Supervisor",
        "logo_url": metadata.get("logo_url"),
        "generated_at": metadata.get("generated_at")
        or datetime.now(timezone.utc).isoformat(),
    }

    if charts:
        payload["charts"] = charts

    pdf_endpoint = base_url.rstrip("/") + "/pdf"
    logger.info("Requesting PDF from %s", pdf_endpoint)
    try:
        response = requests.post(pdf_endpoint, json=payload, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network interaction
        logger.error("Failed to render PDF: %s", exc)
        raise SystemExit(1) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    logger.info("Saved PDF to %s", output_path)

def _generate_document_plan(llm: ChatOpenAI, task: str, report_text: str) -> Dict[str, Any]:
    """Use the LLM to derive PDF framing metadata and chart blueprints."""

    instruction = (
        "You produce structured metadata for executive PDF briefings. "
        "Return only valid JSON following this schema: {"
        "\"title\": str, \"subtitle\": str, \"summary\": str, "
        "\"prepared_for\": str, \"prepared_by\": str, \"logo_url\": str|null, "
        "\"charts\": [ { \"title\": str, \"caption\": str, "
        "\"chart_type\": \"bar\"|\"line\"|\"area\", \"x_labels\": [str], "
        "\"series\": [ { \"name\": str, \"values\": [number] } ] } ] }. "
        "Keep summary under 90 words. Provide 1-3 charts using 3-6 data points that align with the report."
    )

    messages = [
        SystemMessage(content=instruction),
        HumanMessage(
            content=(
                "Task prompt:\n"
                + task
                + "\n\nFinal report:\n"
                + report_text
                + "\n\nRespond with JSON only."
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content if isinstance(response.content, str) else "".join(response.content)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1].strip()
        plan = json.loads(content)
    except Exception as exc:  # pragma: no cover - network/LLM variability
        logger.error("Metadata generation failed (%s); using defaults", exc)
        plan = {
            "title": "EV Market Supervisor Report",
            "subtitle": "Automated Insights",
            "summary": (report_text.splitlines()[0][:280] if report_text else ""),
            "prepared_for": "Executive Stakeholders",
            "prepared_by": "EV Market Supervisor",
            "logo_url": None,
            "charts": [],
        }

    plan.setdefault("title", "EV Market Supervisor Report")
    plan.setdefault("subtitle", "Executive Briefing")
    plan.setdefault("summary", "")
    plan.setdefault("prepared_for", "Executive Stakeholders")
    plan.setdefault("prepared_by", "EV Market Supervisor")
    plan.setdefault("logo_url", None)
    plan.setdefault("charts", [])
    plan["generated_at"] = datetime.now(timezone.utc).isoformat()
    return plan


def _build_chart_images(chart_specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    charts: List[Dict[str, Any]] = []
    for spec in chart_specs[:4]:
        try:
            charts.append(_render_chart_image(spec))
        except Exception as exc:  # pragma: no cover - chart rendering edge cases
            logger.warning("Skipping chart '%s': %s", spec.get("title"), exc)
    return charts


def _render_chart_image(spec: Dict[str, Any]) -> Dict[str, Any]:
    import matplotlib.pyplot as plt

    chart_type = (spec.get("chart_type") or "bar").lower()
    x_labels: List[str] = [str(label) for label in spec.get("x_labels", [])]
    series_list: List[Dict[str, Any]] = spec.get("series", [])

    if not x_labels or not series_list:
        raise ValueError("Chart spec requires x_labels and series data")

    for series in series_list:
        if len(series.get("values", [])) != len(x_labels):
            raise ValueError("Series length mismatch for chart '%s'" % spec.get("title"))

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#f8fafc")

    if chart_type == "line":
        for series in series_list:
            values = [float(v) for v in series.get("values", [])]
            ax.plot(x_labels, values, marker="o", linewidth=2.2, label=series.get("name"))
    elif chart_type == "area":
        for series in series_list:
            values = [float(v) for v in series.get("values", [])]
            ax.fill_between(x_labels, values, alpha=0.32, label=series.get("name"))
            ax.plot(x_labels, values, linewidth=1.6)
    else:
        width = 0.8 / max(len(series_list), 1)
        indices = list(range(len(x_labels)))
        for idx, series in enumerate(series_list):
            offsets = [i + (idx - (len(series_list) - 1) / 2) * width for i in indices]
            values = [float(v) for v in series.get("values", [])]
            ax.bar(offsets, values, width=width, label=series.get("name"))
        ax.set_xticks(indices)
        ax.set_xticklabels(x_labels)

    ax.set_title(spec.get("title", "Market Insight"), fontsize=14, color="#111827", pad=16)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    if any(series.get("name") for series in series_list):
        ax.legend(frameon=False, fontsize=9)

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return {
        "title": spec.get("title", "Chart"),
        "caption": spec.get("caption"),
        "image_base64": encoded,
        "media_type": "image/png",
    }


__all__ = ["build_workflow", "run_supervisor_task", "run_supervisor_state"]


if __name__ == "__main__":
    main()
