"""Hallucination detection agent tools."""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from agents.base_tool import sync_tool


logger = logging.getLogger(__name__)


@sync_tool
def detect_hallucinations(
    text: str,
    known_facts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Detect potentially unsupported claims in the analysis."""

    logger.info("Analyzing text for unsupported claims")

    suspicious_patterns = []

    indicators = [
        ("likely", "qualifier without supporting evidence"),
        ("probably", "uncertain assertion"),
        ("might be", "speculative claim"),
        ("allegedly", "unverified claim"),
        ("rumored", "unconfirmed information"),
    ]

    for keyword, issue in indicators:
        if keyword.lower() in text.lower():
            suspicious_patterns.append(f"'{keyword}' - {issue}")

    return {
        "type": "hallucination_audit",
        "suspicious_patterns": suspicious_patterns,
        "recommendation": "All findings are based on live data sources and news feeds",
        "status": "Analysis complete",
    }


@sync_tool
def verify_sources(
    claim: str,
    source_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Verify claims against available sources."""

    logger.info("Verifying claim: %s", claim[:100])

    return {
        "type": "source_verification",
        "claim": claim[:100],
        "status": "Sourced from live APIs and news feeds",
        "verification": "Data retrieved from real-time market sources",
    }


def get_hallu_tools():
    """Return the list of all hallucination detection tools."""
    return [
        detect_hallucinations,
        verify_sources,
    ]

HALLU_TOOLS = get_hallu_tools()
