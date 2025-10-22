"""Entry point for assembling the simplified EV Market Supervisor workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional

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
) -> Any:
    """Configure the agents, tools, and supervisor loop for a supplied LLM."""

    analysis_prompts = _build_analysis_prompt_lookup()
    validation_prompts = _build_validation_prompt_lookup()

    analysis_tools = list(get_analysis_tools())
    validation_tools = list(get_validation_tools())

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


DEV_TODO: tuple[str, ...] = (
    "Hook `tools.query_market_data` into EV-Volumes, BloombergNEF, or another EV sales dataset.",
    "Connect `tools.fetch_policy_updates` to trusted feeds (DOE AFDC, IEA Global EV Outlook, EU Commission notices).",
    "Integrate `tools.get_oem_insights` with OEM investor relations filings (SEC EDGAR, LSE RNS) or supply-side news APIs.",
    "Power `tools.supply_chain_heatmap` with logistics providers such as Panjiva, Flexport, or in-house supplier scorecards.",
    "Back `tools.finance_dashboard` with market data (Capital IQ, FactSet, Yahoo Finance API) for funding and valuation metrics.",
    "Implement `tools.compile_report` to stitch agent notes into your reporting template and push to the publication channel.",
    "Send `tools.audit_log` events to the observability stack (Datadog, ELK, OpenTelemetry collector) for traceability.",
)


__all__ = ["build_workflow", "DEV_TODO"]
