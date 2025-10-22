"""Minimal tool stubs exposed to the EV Market Intelligence agents."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

Tool = Callable[..., Any]


def query_market_data(query: str) -> str:
    """Retrieve structured EV market data matching the query."""

    raise NotImplementedError(
        "Connect this stub to the data warehouse, API, or analytics view that serves market insights."
    )


def fetch_policy_updates(region: str) -> str:
    """Return the latest regulatory and policy changes for the region."""

    raise NotImplementedError(
        "Wire this tool to your policy tracking feeds or document repositories."
    )


def get_oem_insights(manufacturer: str) -> str:
    """Provide OEM production plans, partnerships, and roadmap intel."""

    raise NotImplementedError(
        "Integrate with OEM disclosures, trusted news sources, or analyst research."
    )


def supply_chain_heatmap(component: str) -> str:
    """Highlight supply chain risks for the specified component."""

    raise NotImplementedError(
        "Aggregate logistics, lead-time, and supplier health signals for this component."
    )


def finance_dashboard(metric: str) -> str:
    """Surface the requested EV financial KPIs."""

    raise NotImplementedError(
        "Connect to the financial data lake or BI dashboards that house these KPIs."
    )


def compile_report(sections: Mapping[str, str]) -> str:
    """Combine agent notes into a final narrative report."""

    raise NotImplementedError(
        "Transform the provided section content into a customer-ready report format."
    )


def audit_log(event: str, payload: Mapping[str, Any]) -> None:
    """Persist supervisor decisions or agent outputs to an audit sink."""

    raise NotImplementedError(
        "Send the event and payload to your observability stack or governance store."
    )


def get_analysis_tools() -> Sequence[Tool]:
    """Return the tool registry shared by the analysis agents."""

    return (
        query_market_data,
        fetch_policy_updates,
        get_oem_insights,
        supply_chain_heatmap,
        finance_dashboard,
    )


def get_validation_tools() -> Sequence[Tool]:
    """Return the tool registry used during validation passes."""

    return (compile_report, audit_log)
