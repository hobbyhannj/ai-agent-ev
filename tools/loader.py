"""Dynamic tool loader for the EV Market Intelligence Supervisor."""

from __future__ import annotations

import importlib
import pkgutil
from collections import defaultdict
from types import ModuleType
from typing import Any, Dict, Mapping, Sequence


def _discover_modules(prefix: str = "tools") -> list[ModuleType]:
    """Find all modules under the tools package."""
    return [
        importlib.import_module(f"{prefix}.{name}")
        for _, name, ispkg in pkgutil.iter_modules(["tools"])
        if not ispkg and name not in {"__init__", "loader"}
    ]


def _merge_tool_mapping(
    target: Dict[str, list[Any]],
    new_tools: Mapping[str, Sequence[Any]] | Sequence[Any],
    *,
    category: str,
    module_name: str,
) -> None:
    if isinstance(new_tools, Mapping):
        for agent, funcs in new_tools.items():
            target[agent].extend(funcs)
    else:  # pragma: no cover - legacy support
        raise TypeError(
            f"Module '{module_name}' returned a non-mapping for {category} tools;"
            " expected a dict keyed by agent name."
        )


def auto_load_tools(category: str) -> Dict[str, tuple[Any, ...]]:
    """Automatically gather all tool functions for a given category keyed by agent."""

    if category not in {"analysis", "validation"}:
        raise ValueError(f"Unsupported tool category: {category}")

    aggregated: Dict[str, list[Any]] = defaultdict(list)

    getter_name = f"get_{category}_tools"
    for mod in _discover_modules():
        getter = getattr(mod, getter_name, None)
        if getter is None:
            continue
        module_tools = getter()
        _merge_tool_mapping(
            aggregated,
            module_tools,
            category=category,
            module_name=mod.__name__,
        )

    return {agent: tuple(funcs) for agent, funcs in aggregated.items()}
