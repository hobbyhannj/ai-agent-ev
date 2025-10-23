"""Supply chain agent tools for EV component and logistics analysis."""

from __future__ import annotations
import logging
from datetime import date
from typing import Any, Dict, Optional
from agents.base_tool import sync_tool
import requests


logger = logging.getLogger(__name__)


@sync_tool
def explore_ev_supply_chain(
    component: Optional[str] = None,
    region: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch supply chain data from DuckDuckGo (no API key required)."""

    logger.info(
        "Fetching EV supply chain (component=%s, region=%s, timeframe=%s)",
        component,
        region,
        timeframe,
    )

    focus_component = component or "battery"
    focus_region = region or "Global"
    period = timeframe or f"status {date.today():%b %Y}"

    try:
        url = "https://api.duckduckgo.com/"

        component_queries = {
            "battery": "lithium battery supply chain EV 2025",
            "semiconductor": "semiconductor supply chain automotive 2025",
            "motor": "rare earth motor supply chain 2025",
        }

        query = component_queries.get(focus_component.lower(), "EV supply chain")

        params = {
            "q": query,
            "format": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("Results", [])
        summary = f"Supply chain briefing for {focus_component.title()} in {focus_region} ({period}):\n"

        if results:
            for i, result in enumerate(results[:5], 1):
                summary += f"{i}. {result.get('Text', 'N/A')}\n"
        else:
            summary += f"Latest supply chain data for {focus_component}.\n"

        return {
            "type": "ev_supply_chain_brief",
            "component": focus_component.title(),
            "region": focus_region,
            "timeframe": period,
            "summary": summary,
            "source": "DuckDuckGo Search",
            "results_count": len(results),
        }
    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return {
            "type": "ev_supply_chain_brief",
            "component": focus_component.title(),
            "region": focus_region,
            "timeframe": period,
            "summary": f"Unable to fetch supply chain data. Network error.",
            "source": "Offline",
            "error": str(e),
        }


def get_supply_tools():
    """Return the list of all supply chain tools."""
    return [
        explore_ev_supply_chain,
    ]

SUPPLY_TOOLS = get_supply_tools()
