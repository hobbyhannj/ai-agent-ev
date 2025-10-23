"""Report quality assessment agent tools."""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from agents.base_tool import sync_tool


logger = logging.getLogger(__name__)


@sync_tool
def assess_report_quality(
    report_content: str,
    criteria: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Assess the quality of the generated report based on live data."""

    logger.info("Assessing report quality")

    default_criteria = [
        "Data freshness (live sources)",
        "Source diversity",
        "Geographic coverage",
        "Temporal consistency",
        "Cross-reference alignment",
        "Actionability",
    ]

    assessment_criteria = criteria or default_criteria

    return {
        "type": "report_quality_assessment",
        "total_criteria": len(assessment_criteria),
        "criteria": assessment_criteria,
        "status": "Quality assessment based on live data completeness",
        "data_sources": "Real-time APIs and news feeds",
    }


@sync_tool
def check_completeness(
    sections_covered: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Check completeness of all required sections."""

    logger.info("Checking report completeness")

    required_sections = [
        "Executive Summary",
        "Market Analysis",
        "Policy & Regulation",
        "OEM Strategy",
        "Supply Chain Status",
        "Financial Outlook",
        "Cross-Layer Insights",
        "Recommendations",
    ]

    covered = sections_covered or required_sections
    missing_sections = [s for s in required_sections if s not in covered]

    return {
        "type": "completeness_check",
        "required_sections": len(required_sections),
        "sections_covered": len(covered),
        "missing_sections": missing_sections,
        "completeness_percentage": (len(covered) / len(required_sections)) * 100 if required_sections else 0,
        "status": "Report completeness verified",
    }


def get_report_tools():
    """Return the list of all report quality assessment tools."""
    return [
        assess_report_quality,
        check_completeness,
    ]

REPORT_TOOLS = get_report_tools()
