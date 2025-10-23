"""OEM agent tools for EV automaker analysis."""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from agents.base_tool import sync_tool
import requests


logger = logging.getLogger(__name__)


@sync_tool
def explore_oem_strategy(
    oem: Optional[str] = None,
    focus: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch OEM strategy data from DuckDuckGo (no API key required)."""

    logger.info(
        "Fetching OEM strategy (oem=%s, focus=%s)",
        oem,
        focus,
    )

    oem_name = oem or "Tesla"
    focus_area = focus or "production plans and strategy"

    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": f"{oem_name} EV production strategy 2025",
            "format": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("Results", [])
        summary = f"Strategy overview for {oem_name} focused on {focus_area}:\n"

        if results:
            for i, result in enumerate(results[:5], 1):
                summary += f"{i}. {result.get('Text', 'N/A')}\n"
        else:
            summary += f"Latest information about {oem_name} EV strategy.\n"

        return {
            "type": "oem_strategy_snapshot",
            "oem": oem_name,
            "focus": focus_area,
            "summary": summary,
            "source": "DuckDuckGo Search",
            "results_count": len(results),
        }
    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return {
            "type": "oem_strategy_snapshot",
            "oem": oem_name,
            "focus": focus_area,
            "summary": f"Unable to fetch OEM strategy for {oem_name}. Network error.",
            "source": "Offline",
            "error": str(e),
        }


def get_oem_tools():
    """Return the list of all OEM tools."""
    return [
        explore_oem_strategy,
    ]

OEM_TOOLS = get_oem_tools()
