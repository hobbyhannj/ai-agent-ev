"""Policy agent tools for EV regulation and incentive analysis."""

from __future__ import annotations
import logging
from datetime import date
from typing import Any, Dict, Optional
from agents.base_tool import sync_tool
import requests


logger = logging.getLogger(__name__)


@sync_tool
def explore_ev_policy(
    region: Optional[str] = None,
    topic: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch EV policy and regulation data from DuckDuckGo."""

    logger.info(
        "Fetching EV policy (region=%s, topic=%s, timeframe=%s)",
        region,
        topic,
        timeframe,
    )

    region_name = region or "Global"
    focus_topic = topic or "EV policy and incentives"
    period = timeframe or f"updated {date.today():%b %Y}"

    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": f"EV policy regulations {region_name} 2025",
            "format": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("Results", [])
        summary = f"EV policy brief for {region_name} ({period}):\n"

        if results:
            for i, result in enumerate(results[:5], 1):
                summary += f"{i}. {result.get('Text', 'N/A')}\n"
        else:
            summary += f"Latest policy information for {region_name}.\n"

        return {
            "type": "ev_policy_brief",
            "region": region_name,
            "topic": focus_topic,
            "timeframe": period,
            "summary": summary,
            "source": "DuckDuckGo Search",
            "results_count": len(results),
        }
    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return {
            "type": "ev_policy_brief",
            "region": region_name,
            "topic": focus_topic,
            "timeframe": period,
            "summary": f"Unable to fetch policy data for {region_name}. Network error.",
            "source": "Offline",
            "error": str(e),
        }


def get_policy_tools():
    """Return the list of all policy tools."""
    return [
        explore_ev_policy,
    ]

POLICY_TOOLS = get_policy_tools()
