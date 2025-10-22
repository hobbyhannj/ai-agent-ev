"""Tool skeletons for EV Market Intelligence agents."""

from __future__ import annotations

from typing import Any, Dict, List


def query_market_data(query: str) -> str:
    """Placeholder tool for retrieving structured EV market datasets."""

    raise NotImplementedError("Implement integration with market intelligence data sources.")


def fetch_policy_updates(region: str) -> str:
    """Placeholder tool returning the latest policy and regulation summaries."""

    raise NotImplementedError("Connect to official policy repositories or feeds.")


def get_oem_insights(manufacturer: str) -> str:
    """Placeholder tool providing OEM production and roadmap intelligence."""

    raise NotImplementedError("Ingest OEM disclosures, earnings calls, or trusted datasets.")


def supply_chain_heatmap(component: str) -> str:
    """Placeholder tool highlighting supply chain risk indicators."""

    raise NotImplementedError("Aggregate logistics, lead time, and supplier status signals.")


def finance_dashboard(metric: str) -> str:
    """Placeholder tool surfacing financial KPIs for the EV ecosystem."""

    raise NotImplementedError("Link to finance data providers or bespoke analytics.")


def compile_report(sections: Dict[str, str]) -> str:
    """Placeholder utility combining agent notes into a final report draft."""

    raise NotImplementedError("Transform section notes into a polished narrative.")


def audit_log(event: str, payload: Dict[str, Any]) -> None:
    """Placeholder tool for persisting supervisor decisions and agent outputs."""

    raise NotImplementedError("Record actions in your chosen observability stack.")


def list_analysis_tools() -> List[Any]:
    """Return the placeholder tool registry for analysis agents."""

    return [
        query_market_data,
        fetch_policy_updates,
        get_oem_insights,
        supply_chain_heatmap,
        finance_dashboard,
    ]


def list_validation_tools() -> List[Any]:
    """Return the placeholder tool registry used during validation steps."""

    return [compile_report, audit_log]
