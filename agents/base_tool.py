from __future__ import annotations
from typing import Any, Callable, Dict
from langchain_core.tools import tool


def sync_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to wrap sync functions as LangGraph @tool compatible."""
    return tool(func)


def dummy_network_call(name: str, delay: float = 0.2) -> Dict[str, Any]:
    """Mock utility to simulate async data fetch."""
    return {"source": name, "data": f"Simulated async call from {name}", "delay": delay}
