"""Market data exploration tool for EV intelligence agents."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


_MARKET_DATA: Dict[str, Dict[str, Any]] = {
    "global": {
        "sales_yoy": "+28% YoY (2024 YTD)",
        "oem_focus": "BYD, Tesla, and Geely are pacing deliveries; Volkswagen regaining share in Europe",
        "drivers": "Battery cost deflation (~$96/kWh) and expanded charging corridors in the EU & US",
        "risks": "Price wars compressing margins; supply-side pressure on graphite and high-nickel cathodes",
    },
    "china": {
        "sales_yoy": "+32% YoY with >9.5M units expected",
        "oem_focus": "BYD Song/Seal families dominate; Li Auto strong in EREV premium segment",
        "drivers": "Tier-2 incentives in Guangdong, battery swap pilots accelerating",
        "risks": "Overcapacity in Tier-3 cities and inventory build-up at dealerships",
    },
    "europe": {
        "sales_yoy": "+16% YoY; plug-in share ~24%",
        "oem_focus": "VW ID family stabilising, Stellantis launching mid-priced EV vans",
        "drivers": "EU CO₂ fleet targets for 2025 and expanding MCS megawatt charging",
        "risks": "Retail demand softness in Germany as Umweltbonus phases out",
    },
    "united states": {
        "sales_yoy": "+19% YoY; 1.9M LDV EVs projected",
        "oem_focus": "Tesla Model Y still leading; GM ramping Ultium SUVs; Hyundai/Kia expanding US output",
        "drivers": "IRA clean vehicle credits + utility-led charging rebates",
        "risks": "Dealer pushback on EV allocations and slow permitting for DC fast charging",
    },
}


def _normalize_region(region: Optional[str]) -> str:
    if not region:
        return "global"
    return region.strip().lower()


def _segment_hint(segment: Optional[str]) -> str:
    if not segment:
        return "broad EV demand, pricing, and OEM share"
    return segment.strip()


def explore_ev_market(
    region: Optional[str] = None,
    segment: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a structured snapshot of EV market activity for a region/segment."""

    logger.info(
        "Exploring EV market (region=%s, segment=%s, timeframe=%s)",
        region,
        segment,
        timeframe,
    )
    region_key = _normalize_region(region)
    market = _MARKET_DATA.get(region_key, _MARKET_DATA["global"])
    label_region = region.title() if region else "Global"
    period = timeframe or f"through {date.today():%b %Y}"

    summary_lines = [
        f"EV market overview for {label_region} ({period}) focused on {_segment_hint(segment)}:",
        f" • Sales growth: {market['sales_yoy']}",
        f" • Leading OEMs: {market['oem_focus']}",
        f" • Demand drivers: {market['drivers']}",
        f" • Watch risks: {market['risks']}",
    ]

    return {
        "type": "ev_market_snapshot",
        "region": label_region,
        "segment": segment or "all",
        "timeframe": period,
        "summary": "\n".join(summary_lines),
        "metrics": market,
    }


def get_analysis_tools() -> dict[str, tuple[Any, ...]]:
    """Return market exploration tools keyed by agent name."""
    return {"market": (explore_ev_market,)}
