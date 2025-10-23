"""Validation and reporting tools."""

from typing import Any, Mapping


def build_report(sections: Mapping[str, str]) -> str:
    """Combine agent notes into a simple markdown report."""

    ordered = [f"## {title}\n{body.strip()}" for title, body in sections.items()]
    return "\n\n".join(ordered)


def log_audit_event(event: str, payload: Mapping[str, Any]) -> None:
    """Send audit events to observability backend (console stub)."""

    print(f"[AUDIT_LOG] Event={event} Payload={dict(payload)}")


def get_validation_tools() -> dict[str, tuple[Any, ...]]:
    """Return validation-related tools keyed by agent name."""

    return {
        "cross_layer_validation": (),
        "report_quality_check": (build_report,),
        "hallucination_check": (log_audit_event,),
    }
