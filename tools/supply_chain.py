"""Supply chain intelligence tool for EV analysis."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


_SUPPLY_CHAIN_DATA: Dict[str, Dict[str, Any]] = {
    "battery": {
        "status": "Battery-grade lithium carbonate spot prices have stabilised at ~$13/kg",
        "disruptions": "Australian spodumene shipments recovering after Q1 weather impacts",
        "mitigations": "OEMs co-investing in cathode plants (Ford-SK On, Stellantis-Nexeon)",
    },
    "semiconductor": {
        "status": "Automotive microcontroller inventories back to 10-12 weeks",
        "disruptions": "Storm-related downtime at fabs in Taiwan added minor delays in Q2",
        "mitigations": "Tier-1s pursuing diversified sourcing via Infineon and Renesas dual-sourcing",
    },
    "motor": {
        "status": "Permanent magnet supply tightness easing as NdPr prices fall 18% YTD",
        "disruptions": "Logistics bottlenecks at Ningbo port briefly affected drive-unit exports",
        "mitigations": "Shift toward induction motors in mid-segment SUVs to reduce rare earth dependency",
    },
}


def explore_ev_supply_chain(
    component: Optional[str] = None,
    region: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a structured supply-chain briefing for a component/region."""

    logger.info(
        "Exploring EV supply chain (component=%s, region=%s, timeframe=%s)",
        component,
        region,
        timeframe,
    )
    key = (component or "battery").strip().lower()
    insight = _SUPPLY_CHAIN_DATA.get(key, _SUPPLY_CHAIN_DATA["battery"])
    focus_component = component.title() if component else "Battery materials"
    focus_region = region.title() if region else "Global"
    period = timeframe or f"status {date.today():%b %Y}"

    return {
        "type": "ev_supply_chain_brief",
        "component": focus_component,
        "region": focus_region,
        "timeframe": period,
        "status": insight["status"],
        "disruptions": insight["disruptions"],
        "mitigations": insight["mitigations"],
    }


def get_analysis_tools() -> dict[str, tuple[Any, ...]]:
    """Return supply-chain exploration tool keyed by agent name."""
    return {"supply_chain": (explore_ev_supply_chain,)}
