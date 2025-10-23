"""EV policy and regulation exploration tool."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


_POLICY_DATA: Dict[str, Dict[str, Any]] = {
    "global": {
        "headline": "Global regulators keep tightening zero-emission targets",
        "highlights": [
            "UNFCCC transport coalition aligning 2035 light-duty zero-emission pledge",
            "30+ countries now require battery passport disclosures from 2025",
        ],
    },
    "china": {
        "headline": "China extends NEV purchase tax waiver to 2027",
        "highlights": [
            "MIIT introduces credit multiplier for <12kWh/100km efficiency",
            "Guangdong and Shanghai increase charging capex support by JPY 10B",
        ],
    },
    "europe": {
        "headline": "EU advances Euro 7 compromise and Critical Raw Materials Act",
        "highlights": [
            "Euro 7 keeps stricter brake/tyre particle limits from 2025",
            "CRM Act targets 65% recycling for battery materials by 2030",
        ],
    },
    "united states": {
        "headline": "US Treasury finalises 2025 IRA foreign entity rules",
        "highlights": [
            "Battery components with FEOC content lose $3,750 credit from 2025",
            "DOE conditionally awards $1.7B ATVM loans for retooling legacy plants",
        ],
    },
}


def explore_ev_policy(
    region: Optional[str] = None,
    topic: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a synthetic policy intelligence brief for the requested scope."""

    logger.info(
        "Exploring EV policy (region=%s, topic=%s, timeframe=%s)",
        region,
        topic,
        timeframe,
    )
    region_key = (region or "global").strip().lower()
    policy = _POLICY_DATA.get(region_key, _POLICY_DATA["global"])
    label_region = region.title() if region else "Global"
    focus_topic = topic or "EV incentives and regulatory landscape"
    period = timeframe or f"updated {date.today():%b %Y}"

    return {
        "type": "ev_policy_brief",
        "region": label_region,
        "topic": focus_topic,
        "timeframe": period,
        "headline": policy["headline"],
        "highlights": policy["highlights"],
    }


def get_analysis_tools() -> dict[str, tuple[Any, ...]]:
    """Return EV policy exploration tool keyed by agent name."""
    return {"policy": (explore_ev_policy,)}
