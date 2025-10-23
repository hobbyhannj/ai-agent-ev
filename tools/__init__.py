"""Unified tool registry for EV Market Intelligence system."""

from __future__ import annotations

import os
from pathlib import Path

from .loader import auto_load_tools

__all__ = [
    "get_analysis_tools",
    "get_validation_tools",
]


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"\'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()


def get_analysis_tools():
    """Dynamically load all analysis tool modules."""
    return auto_load_tools(category="analysis")


def get_validation_tools():
    """Dynamically load all validation tool modules."""
    return auto_load_tools(category="validation")
